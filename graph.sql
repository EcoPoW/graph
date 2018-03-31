CREATE TABLE `graph` (
  `id` int(11) unsigned NOT NULL AUTO_INCREMENT,
  `hash` varchar(128) NOT NULL DEFAULT '',
  `from_block` varchar(128) NOT NULL DEFAULT '',
  `to_block` varchar(128) NOT NULL DEFAULT '',
  `nonce` int(10) unsigned NOT NULL,
  `sender` varchar(128) NOT NULL,
  `receiver` varchar(128) NOT NULL,
  `data` text NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `hash` (`hash`),
  UNIQUE KEY `from_to_block_nonce` (`from_block`,`to_block`,`nonce`),
  KEY `from_block` (`from_block`),
  KEY `to_block` (`to_block`),
  KEY `sender` (`sender`),
  KEY `receiver` (`receiver`)
) ENGINE=InnoDB AUTO_INCREMENT=1 DEFAULT CHARSET=utf8;