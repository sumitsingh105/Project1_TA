import json
import re

# -------------------------
# Utility: Clean post content
# -------------------------
def clean_text(text):
    if not text:
        return ""
    text = re.sub(r"\n{3,}", "\n\n", text)  # collapse excessive newlines
    text = re.sub(r"[^\x00-\x7F]+", "", text)  # remove non-ASCII chars (optional)
    return text.strip()

# -------------------------
# Step 1: Extract context for each post
# -------------------------
def extract_context(posts, current_index, n_context=3):
    context = []
    for i in range(max(0, current_index - n_context), current_index):
        context.append({
            "post_number": posts[i].get("post_number", ""),
            "username": posts[i].get("username", ""),
            "content": posts[i].get("content", ""),
            "created_at": posts[i].get("created_at", "")
        })
    return context

# -------------------------
# Step 2: Add context to posts
# -------------------------
def add_context_to_posts(posts, n_context=3):
    for i, post in enumerate(posts):
        post["thread_context"] = extract_context(posts, i, n_context)
    return posts

# -------------------------
# Step 3: Build RAG-compatible documents
# -------------------------
def build_rag_docs(posts):
    rag_docs = []
    for post in posts:
        content = clean_text(post.get("content", ""))
        thread_title = clean_text(post.get("thread_title", ""))
        thread_context = "\n\n".join(
            f"{ctx['username']}: {clean_text(ctx['content'])}" 
            for ctx in post.get("thread_context", [])
        )
        
        full_text = f"{thread_title}\n\n{thread_context}\n\n{post.get('username')}: {content}"

        doc = {
            "id": f"{post.get('thread_id', 'unknown')}_{post.get('post_number', 'unknown')}",
            "text": full_text.strip(),
            "meta": {
                "thread_id": post.get("thread_id", "unknown"),
                "post_number": post.get("post_number", "unknown"),
                "username": post.get("username", "unknown"),
                "created_at": post.get("created_at", ""),
                "url": post.get("post_url", ""),
                "category": post.get("category_id", None),
                "title": thread_title,
                "image_paths": post.get("image_paths", [])  # <-- included image paths here
            }
        }
        rag_docs.append(doc)
    return rag_docs

# -------------------------
# Entry Point
# -------------------------
def main():
    input_path = "tds_discourse_rich_thread_aware_with_images.jsonl"  # your scraped output file
    output_path = "rag_documents.jsonl"

    with open(input_path, "r", encoding="utf-8") as f:
        posts = [json.loads(line) for line in f]

    posts_with_context = add_context_to_posts(posts)
    rag_docs = build_rag_docs(posts_with_context)

    with open(output_path, "w", encoding="utf-8") as f:
        for doc in rag_docs:
            f.write(json.dumps(doc, ensure_ascii=False) + "\n")

    print(f"✅ RAG documents written to: {output_path} (Total: {len(rag_docs)})")

if __name__ == "__main__":
    main()
