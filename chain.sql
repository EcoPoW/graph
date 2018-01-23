CREATE TABLE `chain` (
  `id` int(11) unsigned NOT NULL AUTO_INCREMENT,
  `hash` varchar(64) NOT NULL DEFAULT '',
  `prev_hash` varchar(64) NOT NULL DEFAULT '',
  `nonce` int(11) unsigned NOT NULL,
  `wallet_id` varchar(32) NOT NULL DEFAULT '',
  `data` mediumtext NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=29 DEFAULT CHARSET=utf8;