-- 旧记录保留在知心畅聊；今后的通识课对话单独保存。
SET @has_scene = (SELECT COUNT(*) FROM information_schema.COLUMNS
  WHERE TABLE_SCHEMA = DATABASE() AND TABLE_NAME = 'chat_history' AND COLUMN_NAME = 'scene');
SET @scene_sql = IF(@has_scene = 0,
  'ALTER TABLE chat_history ADD COLUMN scene VARCHAR(20) NOT NULL DEFAULT ''companion'', ADD INDEX idx_chat_scene (student_id, scene, id)',
  'SELECT 1');
PREPARE scene_stmt FROM @scene_sql;
EXECUTE scene_stmt;
DEALLOCATE PREPARE scene_stmt;
