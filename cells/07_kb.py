# ---- KNOWLEDGE BASE ----
# the library of our support system — like a team's video analysis room

# sample KB data — in real life this would come from a database
SAMPLE_KB_DATA = [
    {
        "id": "kb_001",
        "text": "To reset your password: Go to Settings > Security > Change Password. Enter your current password, then your new password twice. Click Save. If you forgot your password, click 'Forgot Password' on the login page and check your email.",
        "content_tier": "simplified",
        "category": "account",
    },
    {
        "id": "kb_002",
        "text": "API Rate Limiting: Our API enforces rate limits of 1000 requests/minute for Pro plans and 100 requests/minute for Free plans. When rate limited, you'll receive HTTP 429 with a Retry-After header. Implement exponential backoff: start with 1s delay, double on each retry, max 32s. Example: curl -H 'Authorization: Bearer TOKEN' https://api.example.com/v2/data",
        "content_tier": "technical_deep",
        "category": "api",
    },
    {
        "id": "kb_003",
        "text": "Billing FAQ: We offer monthly and annual plans. Annual plans save 20%. To upgrade: Dashboard > Billing > Change Plan. Refunds are available within 14 days of purchase. For enterprise pricing, contact sales@example.com.",
        "content_tier": "simplified",
        "category": "billing",
    },
    {
        "id": "kb_004",
        "text": "Platform SLA: We guarantee 99.9% uptime for Enterprise plans. Current month uptime: 99.95%. Mean response time: 145ms (P95: 320ms). Incident response: P1 within 15min, P2 within 1hr. SLA credits: 10% for each 0.1% below target. Compliance: SOC2 Type II, GDPR, HIPAA ready.",
        "content_tier": "executive_summary",
        "category": "platform",
    },
    {
        "id": "kb_005",
        "text": "OAuth2 PKCE Flow Implementation: 1) Generate code_verifier (43-128 chars, [A-Za-z0-9-._~]). 2) Create code_challenge = BASE64URL(SHA256(code_verifier)). 3) Authorization request: GET /authorize?response_type=code&client_id=CLIENT&code_challenge=CHALLENGE&code_challenge_method=S256. 4) Exchange code: POST /token with code, code_verifier, grant_type=authorization_code. Common error: invalid_grant usually means code_verifier mismatch or expired auth code (5min TTL).",
        "content_tier": "technical_deep",
        "category": "authentication",
    },
    {
        "id": "kb_006",
        "text": "Getting Started Guide: Welcome! To set up your account: 1) Click 'Sign Up' on our homepage. 2) Enter your email and create a password. 3) Verify your email by clicking the link we send. 4) Complete your profile. 5) You're ready to go! Need help? Live chat is available 9am-5pm EST.",
        "content_tier": "simplified",
        "category": "onboarding",
    },
    {
        "id": "kb_007",
        "text": "Webhook Configuration: Set up webhooks at Dashboard > Integrations > Webhooks. Supported events: user.created, payment.completed, subscription.cancelled. Payload format: JSON with HMAC-SHA256 signature in X-Signature header. Verify: hash = HMAC(payload, webhook_secret). Retry policy: 3 attempts with exponential backoff. Debug: Check webhook logs at /dashboard/webhooks/logs.",
        "content_tier": "technical_deep",
        "category": "integrations",
    },
    {
        "id": "kb_008",
        "text": "Enterprise ROI Report: Average customer sees 40% reduction in support ticket volume after implementing our AI assistant. Mean time to resolution decreased by 62%. Customer satisfaction scores improved from 3.2 to 4.6 out of 5. Annual cost savings: $150,000-$500,000 depending on team size. Implementation timeline: 2-4 weeks.",
        "content_tier": "executive_summary",
        "category": "enterprise",
    },
    {
        "id": "kb_009",
        "text": "Security Incident Response: If you suspect unauthorized access: 1) Immediately change your password. 2) Enable 2FA at Settings > Security > Two-Factor Auth. 3) Review active sessions at Settings > Security > Active Sessions and revoke unknown ones. 4) Contact security@example.com. 5) We will investigate within 24 hours and provide a detailed report.",
        "content_tier": "simplified",
        "category": "security",
    },
    {
        "id": "kb_010",
        "text": "Refund Policy: Full refund available within 14 days of purchase, no questions asked. After 14 days, prorated refund for annual plans. Monthly plans: no refund after billing cycle starts. Process: Dashboard > Billing > Request Refund, or email billing@example.com. Processing time: 5-10 business days.",
        "content_tier": "simplified",
        "category": "billing",
    },
]


def ingest_kb_to_pinecone():
    """KB data ko pinecone mein daal do — one time setup"""
    messi_logger.info("Starting KB ingestion to Pinecone...")

    try:
        # pehle check karo ki already data hai ya nahi
        stats = pitch_index.describe_index_stats()
        # pinecone v5 returns object, not dict — pehle stats["total_vector_count"] try kiya tha
        # KeyError aa gaya tha lol
        total_vectors = getattr(stats, 'total_vector_count', 0) if hasattr(stats, 'total_vector_count') else stats.get("total_vector_count", 0)

        if total_vectors > 0:
            messi_logger.info(f"Already {total_vectors} vectors in index, skipping ingestion")
            print(f"Index already has {total_vectors} vectors — skipping ingestion")
            return True

        # embed karo using pinecone inference
        texts_to_embed = [item["text"] for item in SAMPLE_KB_DATA]

        embeddings = pc.inference.embed(
            model=RONALDO_CONFIG["embed_model"],
            inputs=texts_to_embed,
            parameters={"input_type": "passage"}  # passage for indexing
        )

        # upsert karo pinecone mein
        vectors_to_upsert = []
        for i, item in enumerate(SAMPLE_KB_DATA):
            # embeddings[i].values ya embeddings[i]["values"] — depends on pinecone version
            emb_values = embeddings[i].values if hasattr(embeddings[i], 'values') else embeddings[i]["values"]
            vectors_to_upsert.append({
                "id": item["id"],
                "values": emb_values,
                "metadata": {
                    "text": item["text"],
                    "content_tier": item["content_tier"],
                    "category": item["category"],
                }
            })

        # batch upsert — like substituting multiple players at once
        pitch_index.upsert(vectors=vectors_to_upsert)

        # thoda wait karo for indexing
        time.sleep(2)
        messi_logger.info(f"Ingested {len(vectors_to_upsert)} vectors")
        print(f"Ingested {len(vectors_to_upsert)} KB docs into Pinecone")
        return True

    except Exception as e:
        messi_logger.error(f"Ingestion failed: {e}")
        print(f"KB ingestion failed: {e}")
        return False


def search_kb(query: str, content_tier: str = None, top_k: int = 3) -> List[Dict]:
    """KB mein search karo — 2 pass strategy like chess opening"""
    try:
        # embed the query
        query_embedding = pc.inference.embed(
            model=RONALDO_CONFIG["embed_model"],
            inputs=[query],
            parameters={"input_type": "query"}  # query type for searching
        )

        # get embedding values — pinecone v5 object access
        qvec = query_embedding[0].values if hasattr(query_embedding[0], 'values') else query_embedding[0]["values"]

        # Pass 1 — filtered search (persona-specific tier)
        # like playing a specific opening in chess based on your opponent
        results = []
        if content_tier:
            response = pitch_index.query(
                vector=qvec,
                top_k=top_k,
                include_metadata=True,
                filter={"content_tier": {"$eq": content_tier}}
            )
            # pehle response.get("matches", []) likha tha — KeyError aaya
            # pinecone v5 returns objects not dicts smh
            results = response.matches if hasattr(response, 'matches') else response.get("matches", [])

        # Pass 2 — fallback unfiltered if nothing found
        # like switching to a different formation mid-game
        if not results:
            response = pitch_index.query(
                vector=qvec,
                top_k=top_k,
                include_metadata=True
            )
            results = response.matches if hasattr(response, 'matches') else response.get("matches", [])

        # format results
        kb_docs = []
        for match in results:
            # pinecone v5 match objects have .metadata attribute not ["metadata"]
            # pehle match["metadata"]["text"] likha tha — KeyError: 'text' aa raha tha
            meta = match.metadata if hasattr(match, 'metadata') else match.get("metadata", {})
            score = match.score if hasattr(match, 'score') else match.get("score", 0)
            kb_docs.append({
                "text": meta.get("text", "") if isinstance(meta, dict) else getattr(meta, "text", ""),
                "score": score,
                "tier": meta.get("content_tier", "unknown") if isinstance(meta, dict) else getattr(meta, "content_tier", "unknown"),
                "category": meta.get("category", "unknown") if isinstance(meta, dict) else getattr(meta, "category", "unknown"),
            })

        return kb_docs

    except Exception as e:
        messi_logger.error(f"KB search failed: {e}")
        return []


# run ingestion
ingest_kb_to_pinecone()
