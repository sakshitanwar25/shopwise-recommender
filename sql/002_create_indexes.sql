CREATE INDEX IF NOT EXISTS idx_events_user_ts
ON interaction_events(user_id, event_ts DESC);


CREATE INDEX IF NOT EXISTS idx_events_item_ts
ON interaction_events(item_id, event_ts DESC);


CREATE INDEX IF NOT EXISTS idx_items_category
ON items(category_id);