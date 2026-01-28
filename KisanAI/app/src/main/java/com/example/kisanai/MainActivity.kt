package com.example.kisanai

import android.content.ActivityNotFoundException
import android.content.Intent
import android.net.Uri
import android.os.Bundle
import android.os.Environment
import android.provider.MediaStore
import android.webkit.ValueCallback
import android.webkit.WebChromeClient
import android.webkit.WebView
import android.webkit.WebViewClient
import android.widget.Toast
import androidx.activity.enableEdgeToEdge
import androidx.activity.result.contract.ActivityResultContracts
import androidx.appcompat.app.AppCompatActivity
import androidx.core.content.FileProvider
import androidx.core.view.ViewCompat
import androidx.core.view.WindowInsetsCompat
import java.io.File
import java.io.IOException

class MainActivity : AppCompatActivity() {

    private var fileUploadCallback: ValueCallback<Array<Uri>>? = null
    private var cameraPhotoPath: String? = null

    private val fileChooserLauncher = registerForActivityResult(ActivityResultContracts.StartActivityForResult()) { result ->
        if (fileUploadCallback == null) return@registerForActivityResult

        val results = if (result.resultCode == RESULT_OK) {
            // Check if this was a camera capture
            if (cameraPhotoPath != null) {
                val photoFile = File(cameraPhotoPath!!)
                if (photoFile.exists()) {
                    val photoUri = Uri.fromFile(photoFile)
                    arrayOf(photoUri)
                } else {
                    null
                }
            } else if (result.data != null) {
                // Handle gallery/file picker result
                val dataString = result.data?.dataString
                val clipData = result.data?.clipData

                if (clipData != null) {
                    Array(clipData.itemCount) { i -> clipData.getItemAt(i).uri }
                } else if (dataString != null) {
                    arrayOf(Uri.parse(dataString))
                } else {
                    null
                }
            } else {
                null
            }
        } else {
            null
        }

        fileUploadCallback?.onReceiveValue(results)
        fileUploadCallback = null
        cameraPhotoPath = null
    }

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        enableEdgeToEdge()
        setContentView(R.layout.activity_main)
        ViewCompat.setOnApplyWindowInsetsListener(findViewById(R.id.main)) { v, insets ->
            val systemBars = insets.getInsets(WindowInsetsCompat.Type.systemBars())
            v.setPadding(systemBars.left, systemBars.top, systemBars.right, systemBars.bottom)
            insets
        }

        val myWebView: WebView = findViewById(R.id.webview)
        myWebView.webViewClient = WebViewClient()
        
        myWebView.webChromeClient = object : WebChromeClient() {
            override fun onShowFileChooser(
                webView: WebView?,
                filePathCallback: ValueCallback<Array<Uri>>?,
                fileChooserParams: FileChooserParams?
            ): Boolean {
                if (fileUploadCallback != null) {
                    fileUploadCallback?.onReceiveValue(null)
                    fileUploadCallback = null
                }
                fileUploadCallback = filePathCallback

                // Check if this is a camera request (has capture mode)
                val isCaptureEnabled = fileChooserParams?.isCaptureEnabled ?: false
                
                val intent = if (isCaptureEnabled) {
                    // Create camera intent
                    Intent(MediaStore.ACTION_IMAGE_CAPTURE).also { takePictureIntent ->
                        takePictureIntent.resolveActivity(packageManager)?.also {
                            // Create a temporary file for the photo
                            val photoFile: File? = try {
                                File.createTempFile(
                                    "JPEG_${System.currentTimeMillis()}_",
                                    ".jpg",
                                    getExternalFilesDir(Environment.DIRECTORY_PICTURES)
                                )
                            } catch (ex: IOException) {
                                null
                            }
                            photoFile?.also {
                                val photoURI: Uri = FileProvider.getUriForFile(
                                    this@MainActivity,
                                    "com.example.kisanai.fileprovider",
                                    it
                                )
                                takePictureIntent.putExtra(MediaStore.EXTRA_OUTPUT, photoURI)
                                cameraPhotoPath = it.absolutePath
                            }
                        }
                    }
                } else {
                    // Use default file chooser for gallery
                    fileChooserParams?.createIntent()
                }
                
                try {
                    if (intent != null) {
                        fileChooserLauncher.launch(intent)
                    }
                } catch (e: ActivityNotFoundException) {
                    fileUploadCallback = null
                    Toast.makeText(applicationContext, "Cannot open file chooser", Toast.LENGTH_LONG).show()
                    return false
                }
                return true
            }


            override fun onGeolocationPermissionsShowPrompt(origin: String, callback: android.webkit.GeolocationPermissions.Callback) {
                callback.invoke(origin, true, false)
            }
        }

        myWebView.settings.javaScriptEnabled = true
        myWebView.settings.domStorageEnabled = true
        myWebView.settings.databaseEnabled = true
        myWebView.settings.allowFileAccess = true
        myWebView.settings.allowContentAccess = true
        myWebView.settings.allowFileAccessFromFileURLs = true
        myWebView.settings.allowUniversalAccessFromFileURLs = true
        myWebView.loadUrl("file:///android_asset/index.html")

        // Request Location Permission if not granted
        if (androidx.core.content.ContextCompat.checkSelfPermission(this, android.Manifest.permission.ACCESS_FINE_LOCATION) != android.content.pm.PackageManager.PERMISSION_GRANTED) {
            androidx.core.app.ActivityCompat.requestPermissions(this, arrayOf(android.Manifest.permission.ACCESS_FINE_LOCATION), 1001)
        }
    }

    override fun onBackPressed() {
        val myWebView: WebView = findViewById(R.id.webview)
        if (myWebView.canGoBack()) {
            myWebView.goBack()
        } else {
            super.onBackPressed()
        }
    }
}