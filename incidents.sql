use stardust;

CREATE TABLE incidents (
   id INT AUTO_INCREMENT PRIMARY KEY,
   name VARCHAR(255) NOT NULL,
   email VARCHAR(255) NOT NULL,
   incident_summary TEXT NOT NULL,
   incident_type ENUM('cheating', 'bullying', 'others') NOT NULL DEFAULT 'others'
);

ALTER USER 'appuser'@'localhost' IDENTIFIED WITH mysql_native_password BY 'enter your password';
