CREATE TABLE `leaders` (
  `id` int(11) unsigned NOT NULL AUTO_INCREMENT,
  `hash` varchar(128) NOT NULL DEFAULT '',
  `prev_hash` varchar(128) NOT NULL DEFAULT '',
  `pk` varchar(200) NOT NULL DEFAULT '',
  `nonce` int(10) unsigned NOT NULL,
  `timestamp` int(10) unsigned NOT NULL,
  PRIMARY KEY (`id`),
  KEY `hp` (`hash`,`pk`)
) ENGINE=InnoDB AUTO_INCREMENT=1 DEFAULT CHARSET=utf8;