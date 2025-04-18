CREATE TABLE IF NOT EXISTS `content` (
	`id` int AUTO_INCREMENT NOT NULL UNIQUE,
	`title` varchar(70) NOT NULL UNIQUE,
	`classification` varchar(10) NOT NULL,
	`release_date` date NOT NULL,
	`duration` time NOT NULL,
	`summary` varchar(2180) NOT NULL,
	`url_image` varchar(120) NOT NULL,
	`status` varchar(12) NOT NULL,
	`record_date` timestamp DEFAULT CURRENT_TIMESTAMP,
	`price` float NOT NULL,
	`type` varchar(12) NOT NULL,
	PRIMARY KEY (`id`)
);

CREATE TABLE IF NOT EXISTS `tag` (
	`id` int AUTO_INCREMENT NOT NULL UNIQUE,
	`name` varchar(255) NOT NULL UNIQUE,
	PRIMARY KEY (`id`)
);

CREATE TABLE IF NOT EXISTS `content_tag` (
	`content_id` int NOT NULL,
	`tag_id` int NOT NULL,
	PRIMARY KEY (`content_id`, `tag_id`)
);

CREATE TABLE IF NOT EXISTS `purchase` (
	`id` int AUTO_INCREMENT NOT NULL UNIQUE,
	`user_id` int NOT NULL,
	`payment_method_id` int NOT NULL,
	`content_id` int NOT NULL,
	`unit_price` float NOT NULL,
	`amount` int NOT NULL,
	`purchase_date` timestamp DEFAULT CURRENT_TIMESTAMP,
	PRIMARY KEY (`id`)
);

CREATE TABLE IF NOT EXISTS `wish_list` (
	`id` int AUTO_INCREMENT NOT NULL UNIQUE,
	`user_id` int NOT NULL,
	`date_creation` timestamp DEFAULT CURRENT_TIMESTAMP,
	`name` varchar(255) NOT NULL,
	`content_id` int NOT NULL,
	PRIMARY KEY (`id`)
);

CREATE TABLE IF NOT EXISTS `payment_method` (
	`name` varchar(255) NOT NULL,
	`id` int AUTO_INCREMENT NOT NULL UNIQUE,
	`type` varchar(255) NOT NULL,
	PRIMARY KEY (`id`)
);

CREATE TABLE IF NOT EXISTS `users` (
	`id` int AUTO_INCREMENT NOT NULL UNIQUE,
	`name` varchar(255) NOT NULL,
	`surname` varchar(255) NOT NULL,
	`genre` varchar(255) NOT NULL,
	`date_born` date NOT NULL,
	`date_enrollment` timestamp DEFAULT CURRENT_TIMESTAMP,
	`phone` varchar(255) NOT NULL UNIQUE,
	`email` varchar(255) NOT NULL UNIQUE,
	`password` varchar(255) NOT NULL,
	`role` varchar(255) NOT NULL,
	PRIMARY KEY (`id`)
);

CREATE TABLE IF NOT EXISTS `genre` (
	`id` int AUTO_INCREMENT NOT NULL UNIQUE,
	`name` varchar(255) NOT NULL UNIQUE,
	PRIMARY KEY (`id`)
);

CREATE TABLE IF NOT EXISTS `content_genre` (
	`id` int AUTO_INCREMENT NOT NULL UNIQUE,
	`genre_id` int NOT NULL,
	`content_id` int NOT NULL,
	PRIMARY KEY (`id`)
);

CREATE TABLE IF NOT EXISTS `director` (
	`name` varchar(255) NOT NULL,
	`surname` varchar(255) NOT NULL,
	`id` int AUTO_INCREMENT NOT NULL UNIQUE,
	PRIMARY KEY (`id`)
);

CREATE TABLE IF NOT EXISTS `content_director` (
	`content_id` int NOT NULL,
	`id` int AUTO_INCREMENT NOT NULL UNIQUE,
	`director_id` int NOT NULL,
	PRIMARY KEY (`id`)
);

CREATE TABLE IF NOT EXISTS `user_payment_method` (
	`user_id` int NOT NULL,
	`payment_method_id` int NOT NULL UNIQUE,
	`PRIMARY` int NOT NULL,
	`id` int AUTO_INCREMENT NOT NULL UNIQUE,
	PRIMARY KEY (`id`)
);

ALTER TABLE `content_tag` ADD CONSTRAINT `content_tag_fk0` FOREIGN KEY (`content_id`) REFERENCES `content`(`id`);

ALTER TABLE `content_tag` ADD CONSTRAINT `content_tag_fk2` FOREIGN KEY (`tag_id`) REFERENCES `tag`(`id`);

ALTER TABLE `purchase` ADD CONSTRAINT `purchase_fk1` FOREIGN KEY (`user_id`) REFERENCES `users`(`id`);

ALTER TABLE `purchase` ADD CONSTRAINT `purchase_fk2` FOREIGN KEY (`payment_method_id`) REFERENCES `user_payment_method`(`id`);

ALTER TABLE `purchase` ADD CONSTRAINT `purchase_fk3` FOREIGN KEY (`content_id`) REFERENCES `content`(`id`);
ALTER TABLE `wish_list` ADD CONSTRAINT `wish_list_fk1` FOREIGN KEY (`user_id`) REFERENCES `users`(`id`) ON DELETE CASCADE;

ALTER TABLE `wish_list` ADD CONSTRAINT `wish_list_fk4` FOREIGN KEY (`content_id`) REFERENCES `content`(`id`) ON DELETE CASCADE;

ALTER TABLE `content_genre` ADD CONSTRAINT `content_genre_fk1` FOREIGN KEY (`genre_id`) REFERENCES `genre`(`id`);

ALTER TABLE `content_genre` ADD CONSTRAINT `content_genre_fk2` FOREIGN KEY (`content_id`) REFERENCES `content`(`id`);
ALTER TABLE `user_payment_method` ADD CONSTRAINT `user_payment_method_fk0` FOREIGN KEY (`user_id`) REFERENCES `users`(`id`);

ALTER TABLE `user_payment_method` ADD CONSTRAINT `user_payment_method_fk1` FOREIGN KEY (`payment_method_id`) REFERENCES `payment_method`(`id`);
ALTER TABLE `content_director` ADD CONSTRAINT `content_director_fk0` FOREIGN KEY (`content_id`) REFERENCES `content`(`id`);

ALTER TABLE `content_director` ADD CONSTRAINT `content_director_fk2` FOREIGN KEY (`director_id`) REFERENCES `director`(`id`);