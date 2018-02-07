CREATE TABLE `graph` (
  `id` int(11) unsigned NOT NULL AUTO_INCREMENT,
  `hash` varchar(128) NOT NULL DEFAULT '',
  `prev_hash` varchar(128) NOT NULL DEFAULT '',
  `nonce` int(10) unsigned NOT NULL,
  `data` text NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=3 DEFAULT CHARSET=utf8;