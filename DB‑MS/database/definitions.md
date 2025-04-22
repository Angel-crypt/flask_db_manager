 SHOW CREATE TABLE content;
| content | CREATE TABLE `content` (
  `id` int NOT NULL AUTO_INCREMENT,
  `title` varchar(70) NOT NULL,
  `classification` varchar(10) NOT NULL,
  `release_date` date NOT NULL,
  `duration` time NOT NULL,
  `summary` varchar(2180) NOT NULL,
  `url_image` varchar(120) NOT NULL,
  `status` varchar(12) NOT NULL,
  `record_date` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  `price` float NOT NULL,
  `type` varchar(12) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `id` (`id`),
  UNIQUE KEY `title` (`title`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3 |

SHOW CREATE TABLE content_director;
| content_director | CREATE TABLE `content_director` (
  `content_id` int NOT NULL,
  `id` int NOT NULL AUTO_INCREMENT,
  `director_id` int NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `id` (`id`),
  KEY `content_director_fk0` (`content_id`),
  KEY `content_director_fk2` (`director_id`),
  CONSTRAINT `content_director_fk0` FOREIGN KEY (`content_id`) REFERENCES `content` (`id`),
  CONSTRAINT `content_director_fk2` FOREIGN KEY (`director_id`) REFERENCES `director` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3 |

SHOW CREATE TABLE content_genre;
| content_genre | CREATE TABLE `content_genre` (
  `id` int NOT NULL AUTO_INCREMENT,
  `genre_id` int NOT NULL,
  `content_id` int NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `id` (`id`),
  KEY `content_genre_fk1` (`genre_id`),
  KEY `content_genre_fk2` (`content_id`),
  CONSTRAINT `content_genre_fk1` FOREIGN KEY (`genre_id`) REFERENCES `genre` (`id`),
  CONSTRAINT `content_genre_fk2` FOREIGN KEY (`content_id`) REFERENCES `content` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3 |
