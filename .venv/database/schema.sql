CREATE TABLE IF NOT EXISTS `Content` (
	`id` int AUTO_INCREMENT NOT NULL UNIQUE,
	`title` varchar(255) NOT NULL UNIQUE,
	`classification` varchar(255) NOT NULL,
	`release_date` date NOT NULL,
	`duration` time NOT NULL,
	`summary` varchar(255) NOT NULL,
	`url_image` varchar(255) NOT NULL,
	`stock` int NOT NULL,
	`status` varchar(255) NOT NULL,
	`record_date` timestamp DEFAULT CURRENT_TIMESTAMP,
	`price` float NOT NULL,
	`type` varchar(255) NOT NULL,
	PRIMARY KEY (`id`)
);

CREATE TABLE IF NOT EXISTS `Tag` (
	`id` int AUTO_INCREMENT NOT NULL UNIQUE,
	`name` varchar(255) NOT NULL UNIQUE,
	PRIMARY KEY (`id`)
);

CREATE TABLE IF NOT EXISTS `Content_tag` (
	`content_id` int NOT NULL,
	`tag_id` int NOT NULL,
	PRIMARY KEY (`content_id`, `tag_id`)
);

CREATE TABLE IF NOT EXISTS `Buy` (
	`id` int AUTO_INCREMENT NOT NULL UNIQUE,
	`user_id` int NOT NULL,
	`payment_method_id` int NOT NULL,
	`content_id` int NOT NULL,
	`unit_price` float NOT NULL,
	`amount` int NOT NULL,
	`purchase_date` timestamp DEFAULT CURRENT_TIMESTAMP,
	PRIMARY KEY (`id`)
);

CREATE TABLE IF NOT EXISTS `Wish_list` (
	`id` int AUTO_INCREMENT NOT NULL UNIQUE,
	`user_id` int NOT NULL,
	`date_creation` timestamp DEFAULT CURRENT_TIMESTAMP,
	`name` varchar(255) NOT NULL,
	`content_id` int NOT NULL,
	PRIMARY KEY (`id`)
);

CREATE TABLE IF NOT EXISTS `Payment_method` (
	`name` varchar(255) NOT NULL,
	`id` int AUTO_INCREMENT NOT NULL UNIQUE,
	`type` varchar(255) NOT NULL,
	PRIMARY KEY (`id`)
);

CREATE TABLE IF NOT EXISTS `Users` (
	`id` int AUTO_INCREMENT NOT NULL UNIQUE,
	`name` varchar(255) NOT NULL,
	`surname` varchar(255) NOT NULL,
	`genre` varchar(255) NOT NULL,
	`date_born` date NOT NULL,
	`date_enrollment` timestamp DEFAULT CURRENT_TIMESTAMP,
	`phone` varchar(255) NOT NULL UNIQUE,
	`mail` varchar(255) NOT NULL UNIQUE,
	`password` varchar(255) NOT NULL,
	`rol` varchar(255) NOT NULL,
	PRIMARY KEY (`id`)
);

CREATE TABLE IF NOT EXISTS `Genre` (
	`id` int AUTO_INCREMENT NOT NULL UNIQUE,
	`name` varchar(255) NOT NULL UNIQUE,
	PRIMARY KEY (`id`)
);

CREATE TABLE IF NOT EXISTS `Content_genre` (
	`id` int AUTO_INCREMENT NOT NULL UNIQUE,
	`genre_id` int NOT NULL,
	`content_id` int NOT NULL,
	PRIMARY KEY (`id`)
);

CREATE TABLE IF NOT EXISTS `Director` (
	`name` varchar(255) NOT NULL,
	`surname` varchar(255) NOT NULL,
	`id` int AUTO_INCREMENT NOT NULL UNIQUE,
	PRIMARY KEY (`id`)
);

CREATE TABLE IF NOT EXISTS `Content_director` (
	`content_id` int NOT NULL,
	`id` int AUTO_INCREMENT NOT NULL UNIQUE,
	`director_id` int NOT NULL,
	PRIMARY KEY (`id`)
);

CREATE TABLE IF NOT EXISTS `User_payment_method` (
	`user_id` int NOT NULL,
	`payment_method_id` int NOT NULL UNIQUE,
	`PRIMARY` int NOT NULL,
	`id` int AUTO_INCREMENT NOT NULL UNIQUE,
	PRIMARY KEY (`id`)
);

ALTER TABLE `Content_tag` ADD CONSTRAINT `Content_tag_fk0` FOREIGN KEY (`content_id`) REFERENCES `Content`(`id`);

ALTER TABLE `Content_tag` ADD CONSTRAINT `Content_tag_fk2` FOREIGN KEY (`tag_id`) REFERENCES `Tag`(`id`);

ALTER TABLE `Buy` ADD CONSTRAINT `Buy_fk1` FOREIGN KEY (`user_id`) REFERENCES `Users`(`id`);

ALTER TABLE `Buy` ADD CONSTRAINT `Buy_fk2` FOREIGN KEY (`payment_method_id`) REFERENCES `User_payment_method`(`id`);

ALTER TABLE `Buy` ADD CONSTRAINT `Buy_fk3` FOREIGN KEY (`content_id`) REFERENCES `Content`(`id`);
ALTER TABLE `Wish_list` ADD CONSTRAINT `Wish_list_fk1` FOREIGN KEY (`user_id`) REFERENCES `Users`(`id`) ON DELETE CASCADE;

ALTER TABLE `Wish_list` ADD CONSTRAINT `Wish_list_fk4` FOREIGN KEY (`content_id`) REFERENCES `Content`(`id`) ON DELETE CASCADE;

ALTER TABLE `Content_genre` ADD CONSTRAINT `Content_genre_fk1` FOREIGN KEY (`genre_id`) REFERENCES `Genre`(`id`);

ALTER TABLE `Content_genre` ADD CONSTRAINT `Content_genre_fk2` FOREIGN KEY (`content_id`) REFERENCES `Content`(`id`);
ALTER TABLE `User_payment_method` ADD CONSTRAINT `User_payment_method_fk0` FOREIGN KEY (`user_id`) REFERENCES `Users`(`id`);

ALTER TABLE `User_payment_method` ADD CONSTRAINT `User_payment_method_fk1` FOREIGN KEY (`payment_method_id`) REFERENCES `Payment_method`(`id`);
ALTER TABLE `Content_director` ADD CONSTRAINT `Content_director_fk0` FOREIGN KEY (`content_id`) REFERENCES `Content`(`id`);

ALTER TABLE `Content_director` ADD CONSTRAINT `Content_director_fk2` FOREIGN KEY (`director_id`) REFERENCES `Director`(`id`);