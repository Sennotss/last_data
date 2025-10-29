SOURCES = [
    {
        "source": "news",
        "display_type": 2,
        "status_name": "crawler.google.news_status",
        "collection_name": "topics_formed",
        "with_date_field_date": False,
    },
    {
        "source": "media_cetak",
        "display_type": 2,
        "status_name": "crawler.formed.cetak_status",
        "collection_name": "topics_formed",
        "with_date_field_date": False,
    },
    {
        "source": "media_tv",
        "display_type": 2,
        "status_name": "crawler.formed.tv_status",
        "collection_name": "topics_formed",
        "with_date_field_date": False,
    },
    {
        "source": "radio",
        "display_type": 2,
        "status_name": "crawler.formed.radio_status",
        "collection_name": "topics_formed",
        "with_date_field_date": False,
    },
    {
        "source": "running_text",
        "display_type": 2,
        "status_name": "crawler.formed.running_text_status",
        "collection_name": "topics_formed",
        "with_date_field_date": False,
    },
    {
        "source": "twitter",
        "display_type": 1,
        "status_name": "crawler.twitter.status",
        "collection_name": "topics",
        "with_date_field_date": True,
    },
    {
        "source": "facebook",
        "display_type": 1,
        "status_name": "crawler.facebook.status",
        "collection_name": "topics",
        "with_date_field_date": True,
    },
    {
        "source": "instagram",
        "display_type": 1,
        "status_name": "crawler.instagram.status",
        "collection_name": "topics",
        "with_date_field_date": True,
    },
    {
        "source": "youtube",
        "display_type": 1,
        "status_name": "crawler.youtube.status",
        "collection_name": "topics",
        "with_date_field_date": True,
    },
    {
        "source": "tiktok",
        "display_type": 1,
        "status_name": "crawler.tiktok.status",
        "collection_name": "topics",
        "with_date_field_date": True,
    },
    {
        "source": "review",
        "display_type": 1,
        "status_name": "crawler.review.status",
        "collection_name": "topics",
        "with_date_field_date": True,
    },
    {
        "source": "linkedin",
        "display_type": 1,
        "status_name": "crawler.linkedin.status",
        "collection_name": "topics",
        "with_date_field_date": True,
    },
]


SOURCE_TYPES = {src["source"]: src["display_type"] for src in SOURCES}
