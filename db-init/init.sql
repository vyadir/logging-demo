CREATE TABLE IF NOT EXISTS logs (
  id INT AUTO_INCREMENT PRIMARY KEY,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  logger VARCHAR(255),
  level VARCHAR(50),
  message TEXT,
  pathname VARCHAR(512),
  lineno INT,
  exception TEXT
);
