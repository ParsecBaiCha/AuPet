CREATE TABLE IF NOT EXISTS student_emotions (
  student_id INT NOT NULL,
  emotion_date DATE NOT NULL,
  mood VARCHAR(120) NOT NULL,
  note TEXT,
  PRIMARY KEY (student_id, emotion_date)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE IF NOT EXISTS learning_support_alerts (
  id INT AUTO_INCREMENT PRIMARY KEY,
  student_id INT NOT NULL,
  kind VARCHAR(30) NOT NULL,
  alert_date DATE NOT NULL,
  reason VARCHAR(500) NOT NULL,
  status VARCHAR(20) NOT NULL DEFAULT 'pending',
  created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  UNIQUE KEY daily_signal (student_id, kind, alert_date)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE IF NOT EXISTS student_learning_support (
  student_id INT PRIMARY KEY,
  difficulty VARCHAR(20) NOT NULL DEFAULT 'normal',
  teacher_id INT NOT NULL,
  updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE IF NOT EXISTS learning_support_actions (
  id INT AUTO_INCREMENT PRIMARY KEY,
  alert_id INT NOT NULL,
  student_id INT NOT NULL,
  teacher_id INT NOT NULL,
  action VARCHAR(20) NOT NULL,
  note VARCHAR(500) NOT NULL,
  created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  KEY student_history (student_id, id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
