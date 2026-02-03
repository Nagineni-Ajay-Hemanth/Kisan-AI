# ===========================
# COMMUNITY ENDPOINTS
# ===========================
# This file contains all community-related endpoints
# These functions will be imported into main.py

# Community Models are defined in main.py

def register_community_endpoints(app, get_db_connection, HTTPException):
    """Register all community endpoints with the FastAPI app"""
    
    from pydantic import BaseModel
    
    # Community Models
    class PostCreate(BaseModel):
        title: str
        content: str
        category: str = "question"  # question, tip, discussion

    class ReplyCreate(BaseModel):
        content: str

    # --- Community Posts ---
    @app.post("/community/posts/create")
    def create_community_post(post: PostCreate, user_id: int):
        """Farmer creates a new community post"""
        conn = get_db_connection()
        try:
            cursor = conn.cursor()
            
            # Verify user is a farmer
            cursor.execute("SELECT user_type FROM users WHERE id = ?", (user_id,))
            user = cursor.fetchone()
            if not user or user["user_type"] != "farmer":
                raise HTTPException(status_code=403, detail="Only farmers can create posts")
            
            cursor.execute("""
                INSERT INTO community_posts (farmer_id, title, content, category)
                VALUES (?, ?, ?, ?)
            """, (user_id, post.title, post.content, post.category))
            conn.commit()
            post_id = cursor.lastrowid
            return {"message": "Post created successfully", "post_id": post_id}
        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))
        finally:
            conn.close()

    @app.get("/community/posts/list")
    def list_community_posts(category: str = None, limit: int = 50, offset: int = 0):
        """List all community posts with pagination"""
        conn = get_db_connection()
        cursor = conn.cursor()
        
        if category and category != "all":
            cursor.execute("""
                SELECT p.*, u.username as farmer_name, u.mobile as farmer_mobile
                FROM community_posts p
                JOIN users u ON p.farmer_id = u.id
                WHERE p.category = ?
                ORDER BY p.created_at DESC
                LIMIT ? OFFSET ?
            """, (category, limit, offset))
        else:
            cursor.execute("""
                SELECT p.*, u.username as farmer_name, u.mobile as farmer_mobile
                FROM community_posts p
                JOIN users u ON p.farmer_id = u.id
                ORDER BY p.created_at DESC
                LIMIT ? OFFSET ?
            """, (limit, offset))
        
        posts = [dict(row) for row in cursor.fetchall()]
        conn.close()
        return {"posts": posts}

    @app.get("/community/posts/{post_id}")
    def get_community_post(post_id: int):
        """Get single post with all replies"""
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Get post
        cursor.execute("""
            SELECT p.*, u.username as farmer_name, u.mobile as farmer_mobile
            FROM community_posts p
            JOIN users u ON p.farmer_id = u.id
            WHERE p.id = ?
        """, (post_id,))
        post = cursor.fetchone()
        
        if not post:
            conn.close()
            raise HTTPException(status_code=404, detail="Post not found")
        
        # Get replies
        cursor.execute("""
            SELECT r.*, u.username as farmer_name, u.mobile as farmer_mobile
            FROM community_replies r
            JOIN users u ON r.farmer_id = u.id
            WHERE r.post_id = ?
            ORDER BY r.created_at ASC
        """, (post_id,))
        replies = [dict(row) for row in cursor.fetchall()]
        
        conn.close()
        return {"post": dict(post), "replies": replies}

    @app.post("/community/posts/{post_id}/reply")
    def reply_to_post(post_id: int, reply: ReplyCreate, user_id: int):
        """Add reply to a post"""
        conn = get_db_connection()
        try:
            cursor = conn.cursor()
            
            # Verify user is a farmer
            cursor.execute("SELECT user_type FROM users WHERE id = ?", (user_id,))
            user = cursor.fetchone()
            if not user or user["user_type"] != "farmer":
                raise HTTPException(status_code=403, detail="Only farmers can reply")
            
            # Verify post exists
            cursor.execute("SELECT id FROM community_posts WHERE id = ?", (post_id,))
            if not cursor.fetchone():
                raise HTTPException(status_code=404, detail="Post not found")
            
            # Create reply
            cursor.execute("""
                INSERT INTO community_replies (post_id, farmer_id, content)
                VALUES (?, ?, ?)
            """, (post_id, user_id, reply.content))
            
            # Update replies count
            cursor.execute("""
                UPDATE community_posts 
                SET replies_count = replies_count + 1, updated_at = CURRENT_TIMESTAMP
                WHERE id = ?
            """, (post_id,))
            
            conn.commit()
            reply_id = cursor.lastrowid
            return {"message": "Reply added successfully", "reply_id": reply_id}
        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))
        finally:
            conn.close()

    @app.post("/community/posts/{post_id}/like")
    def like_post(post_id: int, user_id: int):
        """Like/unlike a post"""
        conn = get_db_connection()
        try:
            cursor = conn.cursor()
            
            # Check if already liked
            cursor.execute("""
                SELECT id FROM community_likes 
                WHERE user_id = ? AND post_id = ?
            """, (user_id, post_id))
            existing_like = cursor.fetchone()
            
            if existing_like:
                # Unlike
                cursor.execute("""
                    DELETE FROM community_likes 
                    WHERE user_id = ? AND post_id = ?
                """, (user_id, post_id))
                cursor.execute("""
                    UPDATE community_posts 
                    SET likes_count = likes_count - 1
                    WHERE id = ?
                """, (post_id,))
                liked = False
            else:
                # Like
                cursor.execute("""
                    INSERT INTO community_likes (user_id, post_id)
                    VALUES (?, ?
)
                """, (user_id, post_id))
                cursor.execute("""
                    UPDATE community_posts 
                    SET likes_count = likes_count + 1
                    WHERE id = ?
                """, (post_id,))
                liked = True
            
            # Get updated count
            cursor.execute("SELECT likes_count FROM community_posts WHERE id = ?", (post_id,))
            result = cursor.fetchone()
            likes_count = result["likes_count"] if result else 0
            
            conn.commit()
            return {"liked": liked, "likes_count": likes_count}
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))
        finally:
            conn.close()

    @app.post("/community/replies/{reply_id}/like")
    def like_reply(reply_id: int, user_id: int):
        """Like/unlike a reply"""
        conn = get_db_connection()
        try:
            cursor = conn.cursor()
            
            # Check if already liked
            cursor.execute("""
                SELECT id FROM community_likes 
                WHERE user_id = ? AND reply_id = ?
            """, (user_id, reply_id))
            existing_like = cursor.fetchone()
            
            if existing_like:
                # Unlike
                cursor.execute("""
                    DELETE FROM community_likes 
                    WHERE user_id = ? AND reply_id = ?
                """, (user_id, reply_id))
                cursor.execute("""
                    UPDATE community_replies 
                    SET likes_count = likes_count - 1
                    WHERE id = ?
                """, (reply_id,))
                liked = False
            else:
                # Like
                cursor.execute("""
                    INSERT INTO community_likes (user_id, reply_id)
                    VALUES (?, ?)
                """, (user_id, reply_id))
                cursor.execute("""
                    UPDATE community_replies 
                    SET likes_count = likes_count + 1
                    WHERE id = ?
                """, (reply_id,))
                liked = True
            
            # Get updated count
            cursor.execute("SELECT likes_count FROM community_replies WHERE id = ?", (reply_id,))
            result = cursor.fetchone()
            likes_count = result["likes_count"] if result else 0
            
            conn.commit()
            return {"liked": liked, "likes_count": likes_count}
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))
        finally:
            conn.close()

    @app.delete("/community/posts/{post_id}")
    def delete_community_post(post_id: int, user_id: int):
        """Delete own post"""
        conn = get_db_connection()
        try:
            cursor = conn.cursor()
            
            # Verify ownership
            cursor.execute("SELECT farmer_id FROM community_posts WHERE id = ?", (post_id,))
            result = cursor.fetchone()
            if not result or result["farmer_id"] != user_id:
                raise HTTPException(status_code=403, detail="Not authorized")
            
            # Delete post (replies and likes will cascade)
            cursor.execute("DELETE FROM community_posts WHERE id = ?", (post_id,))
            conn.commit()
            return {"message": "Post deleted successfully"}
        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))
        finally:
            conn.close()

    @app.delete("/community/replies/{reply_id}")
    def delete_community_reply(reply_id: int, user_id: int):
        """Delete own reply"""
        conn = get_db_connection()
        try:
            cursor = conn.cursor()
            
            # Verify ownership and get post_id
            cursor.execute("SELECT farmer_id, post_id FROM community_replies WHERE id = ?", (reply_id,))
            result = cursor.fetchone()
            if not result or result["farmer_id"] != user_id:
                raise HTTPException(status_code=403, detail="Not authorized")
            
            post_id = result["post_id"]
            
            # Delete reply
            cursor.execute("DELETE FROM community_replies WHERE id = ?", (reply_id,))
            
            # Update replies count
            cursor.execute("""
                UPDATE community_posts 
                SET replies_count = replies_count - 1
                WHERE id = ?
            """, (post_id,))
            
            conn.commit()
            return {"message": "Reply deleted successfully"}
        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))
        finally:
            conn.close()
