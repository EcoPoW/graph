CREATE TABLE `transactions` (
  `id` int(11) unsigned NOT NULL AUTO_INCREMENT,
  `txid` varchar(128) NOT NULL,
  `data` text NOT NULL,
  `from_node` varchar(128) NOT NULL DEFAULT '',
  `to_node` varchar(128) NOT NULL DEFAULT '',
  `timestamp` int(11) unsigned NOT NULL,
  PRIMARY KEY (`id`),
  KEY `timestamp` (`timestamp`)
) ENGINE=InnoDB AUTO_INCREMENT=1 DEFAULT CHARSET=utf8;