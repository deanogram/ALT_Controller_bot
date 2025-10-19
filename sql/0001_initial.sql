CREATE TABLE IF NOT EXISTS channels (
    id BIGSERIAL PRIMARY KEY,
    tg_chat_id BIGINT UNIQUE NOT NULL,
    username TEXT,
    title TEXT NOT NULL,
    tz TEXT DEFAULT 'Asia/Tashkent',
    post_interval_min INT DEFAULT 60,
    settings_json JSONB DEFAULT '{}'::jsonb
);

CREATE TABLE IF NOT EXISTS user_channels (
    id BIGSERIAL PRIMARY KEY,
    user_id BIGINT NOT NULL,
    channel_id BIGINT NOT NULL REFERENCES channels(id) ON DELETE CASCADE,
    role TEXT NOT NULL CHECK (role IN ('owner','admin','editor','analyst'))
);

CREATE TABLE IF NOT EXISTS posts (
    id BIGSERIAL PRIMARY KEY,
    author_user_id BIGINT NOT NULL,
    status TEXT NOT NULL DEFAULT 'draft' CHECK (status IN ('draft','scheduled','queued','published','deleted')),
    created_at TIMESTAMPTZ DEFAULT now(),
    updated_at TIMESTAMPTZ,
    scheduled_at TIMESTAMPTZ,
    channels INT[] NOT NULL,
    text TEXT,
    parse_mode TEXT DEFAULT 'HTML' CHECK (parse_mode IN ('HTML','Markdown','None')),
    media_json JSONB,
    buttons_json JSONB,
    reactions_json JSONB,
    preview_message_id BIGINT
);

CREATE TABLE IF NOT EXISTS stats_clicks (
    id BIGSERIAL PRIMARY KEY,
    post_id BIGINT REFERENCES posts(id) ON DELETE CASCADE,
    channel_id BIGINT REFERENCES channels(id) ON DELETE CASCADE,
    button_key TEXT NOT NULL,
    clicks INT DEFAULT 0,
    updated_at TIMESTAMPTZ DEFAULT now()
);

CREATE TABLE IF NOT EXISTS stats_reactions (
    id BIGSERIAL PRIMARY KEY,
    post_id BIGINT REFERENCES posts(id) ON DELETE CASCADE,
    channel_id BIGINT REFERENCES channels(id) ON DELETE CASCADE,
    emoji TEXT NOT NULL,
    count INT DEFAULT 0,
    updated_at TIMESTAMPTZ DEFAULT now()
);

CREATE TABLE IF NOT EXISTS audit (
    id BIGSERIAL PRIMARY KEY,
    user_id BIGINT,
    action TEXT NOT NULL,
    target_type TEXT,
    target_id BIGINT,
    ts TIMESTAMPTZ DEFAULT now(),
    extra_json JSONB
);
