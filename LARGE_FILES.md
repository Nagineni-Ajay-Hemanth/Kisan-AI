# Large Files Download Instructions

Some files are too large to be stored in the Git repository. You'll need to download them separately.

## Required Files

### 1. HWSD2.mdb (88 MB)
**Purpose**: Harmonized World Soil Database - Required for soil analysis feature

**Download Options**:

**Option A: From Google Drive** (Recommended)
- Upload the file to your Google Drive
- Share it and get the link
- Add the link here: `[Download HWSD2.mdb](your-google-drive-link)`

**Option B: From Original Source**
- Visit: https://www.fao.org/soils-portal/data-hub/soil-maps-and-databases/harmonized-world-soil-database-v12/en/
- Download the database
- Extract `HWSD2.mdb` file

**Installation**:
```bash
# Place the file in the project root
/home/ajay/Desktop/Kisan-AI/HWSD2.mdb

# Or on Windows
C:\Users\YourUsername\Documents\Kisan-AI\HWSD2.mdb
```

### 2. backend-server.zip (872 KB)
**Purpose**: Backup of backend server code

**Note**: This is a backup file and not required for running the application. The actual backend code is in the `backend-server/` directory.

## Verification

After downloading, verify the files are in the correct location:

```bash
# Linux/macOS
ls -lh HWSD2.mdb

# Windows
dir HWSD2.mdb
```

## Docker Users

If using Docker, the HWSD2.mdb file will be automatically mounted into the container via docker-compose.yml:

```yaml
volumes:
  - ./HWSD2.mdb:/app/HWSD2.mdb
```

Make sure the file exists in the project root before running `docker-compose up`.

## Alternative: Run Without Soil Database

If you don't have the HWSD2.mdb file, the application will still work but with limited soil analysis capabilities. The system will show a warning in the logs:

```
⚠️  WARNING: HWSD2.mdb not found. Soil analysis may be limited.
```

## File Sizes Reference

- `HWSD2.mdb`: ~88 MB
- `backend-server.zip`: ~872 KB (optional backup)

## Need Help?

If you have issues downloading or installing these files, please open an issue on GitHub.
