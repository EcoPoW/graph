CREATE TABLE `graph` (
  `id` int(11) unsigned NOT NULL AUTO_INCREMENT,
  `hash` varchar(128) NOT NULL DEFAULT '',
  `from_node` varchar(128) NOT NULL DEFAULT '',
  `to_node` varchar(128) NOT NULL DEFAULT '',
  `nonce` int(10) unsigned NOT NULL,
  `sender` varchar(128) NOT NULL,
  `receiver` varchar(128) NOT NULL,
  `data` text NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `hash` (`hash`),
  UNIQUE KEY `from_node` (`from_node`,`to_node`,`nonce`),
  KEY `from_node_2` (`from_node`),
  KEY `to_node` (`to_node`),
  KEY `sender` (`sender`),
  KEY `receiver` (`receiver`)
) ENGINE=InnoDB AUTO_INCREMENT=1 DEFAULT CHARSET=utf8;