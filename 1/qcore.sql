CREATE TABLE `bc_content` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `user_id` int(11) NOT NULL,
  `title` varchar(200) NOT NULL,
  `slug` varchar(200) NOT NULL,
  `created` int(11) DEFAULT NULL,
  `modified` int(11) DEFAULT NULL,
  `text` text,
  `order` int(11) NOT NULL DEFAULT '0',
  `template` varchar(45) DEFAULT NULL,
  `type` varchar(45) NOT NULL DEFAULT 'post',
  `status` varchar(45) NOT NULL DEFAULT 'publish',
  `allow_comment` char(1) NOT NULL DEFAULT '1',
  `allow_ping` char(1) NOT NULL DEFAULT '1',
  `allow_feed` char(1) NOT NULL DEFAULT '1',
  PRIMARY KEY (`id`),
  UNIQUE KEY `IX_slug` (`slug`),
  KEY `IX_created` (`created`)
) ENGINE=MyISAM DEFAULT CHARSET=utf8 COMMENT='内容表';

CREATE TABLE `bc_meta` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `type` varchar(45) NOT NULL DEFAULT 'category' COMMENT 'category:分类\ntage:tage',
  `name` varchar(45) NOT NULL COMMENT '  ',
  `desc` varchar(200) DEFAULT NULL,
  `count` int(11) NOT NULL DEFAULT '0',
  `order` int(11) DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `IX_order` (`order`)
) ENGINE=MyISAM AUTO_INCREMENT=2 DEFAULT CHARSET=utf8;

CREATE TABLE `bc_meta_has_content` (
  `meta_id` int(11) NOT NULL,
  `content_id` int(11) NOT NULL,
  PRIMARY KEY (`meta_id`,`content_id`)
) ENGINE=MyISAM DEFAULT CHARSET=utf8 COMMENT='文章分类关联表';

CREATE TABLE `sys_acl` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `uri` varchar(100) NOT NULL,
  `desc` varchar(45) DEFAULT NULL,
  `deny` varchar(200) DEFAULT NULL,
  `allow` varchar(200) DEFAULT NULL,
  PRIMARY KEY (`id`)
) ENGINE=MyISAM AUTO_INCREMENT=15 DEFAULT CHARSET=utf8 COMMENT='访问控制';

CREATE TABLE `sys_options` (
  `user_id` int(11) NOT NULL DEFAULT '0',
  `name` varchar(32) NOT NULL,
  `value` text,
  PRIMARY KEY (`user_id`,`name`)
) ENGINE=MyISAM DEFAULT CHARSET=utf8 COMMENT='配置表';

CREATE TABLE `uc_role` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `code` varchar(45) NOT NULL,
  `name` varchar(45) NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=MyISAM AUTO_INCREMENT=2 DEFAULT CHARSET=utf8 COMMENT='角色表';

CREATE TABLE `uc_role_has_user` (
  `user_id` int(11) NOT NULL,
  `role_id` int(11) NOT NULL,
  PRIMARY KEY (`user_id`,`role_id`)
) ENGINE=MyISAM DEFAULT CHARSET=utf8 COMMENT='角色用户关联表';

CREATE TABLE `uc_user` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `email` varchar(200) NOT NULL,
  `password` char(35) NOT NULL,
  `nickname` varchar(45) DEFAULT NULL,
  `encryption` char(4) NOT NULL,
  `last_login_time` int(11) DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `IX_email` (`email`)
) ENGINE=MyISAM AUTO_INCREMENT=1 DEFAULT CHARSET=utf8 COMMENT='用户表';

INSERT INTO `uc_role` VALUES ('1', 'admin', '管理员');
INSERT INTO `bc_meta` VALUES ('1', 'category', '默认分类', '这是一个默认分类', '0', null);
INSERT INTO `sys_acl` VALUES ('1', '/admin/role', '角色管理', '[]', '[\"admin\"]');
INSERT INTO `sys_acl` VALUES ('2', '/admin/acl', '访问控制', '[]', '[\"admin\"]');
INSERT INTO `sys_acl` VALUES ('3', '/admin/user', '会员管理', '[]', '[\"admin\"]');
INSERT INTO `sys_acl` VALUES ('4', '/admin/fatArticle', '添加文章', '[]', '[\"admin\"]');
INSERT INTO `sys_acl` VALUES ('5', '/admin/comment', '评论管理', '[]', '[\"admin\"]');
INSERT INTO `sys_acl` VALUES ('6', '/admin/profile', '个人资料', '[]', '[\"admin\"]');
INSERT INTO `sys_acl` VALUES ('7', '/admin/articles', '文章列表', '[]', '[\"admin\"]');
INSERT INTO `sys_acl` VALUES ('8', '/admin/template', '风格设置', '[]', '[\"admin\"]');
INSERT INTO `sys_acl` VALUES ('9', '/admin/option', '基本设置', '[]', '[\"admin\"]');
INSERT INTO `sys_acl` VALUES ('10', '/admin/pages', '页面列表', '[]', '[\"admin\"]');
INSERT INTO `sys_acl` VALUES ('11', '/admin/fatPage', '撰写页面', '[]', '[\"admin\"]');
INSERT INTO `sys_acl` VALUES ('12', '/admin/category', '文章分类', '[]', '[\"admin\"]');
INSERT INTO `sys_acl` VALUES ('13', '/admin/upload', '文件上传', '[]', '[\"admin\"]');
INSERT INTO `sys_acl` VALUES ('14', '/admin/tags', 'tag 管理', '[]', '[\"admin\"]');
INSERT INTO `sys_acl` VALUES ('14', '/admin/plugin', '插件管理', '[]', '[\"admin\"]');
INSERT INTO `sys_options` VALUES ('0', 'site_templates', '\"octopress\"');
INSERT INTO `sys_options` VALUES ('0', 'site', '{\"keywords\": \"sae,ptyhon,blog\", \"title\": \"Qcore\", \"subtitle\": \"\\u4eba\\u751f\\u82e6\\u77ed\\uff0c\\u6211\\u7528python\", \"desc\": \"Qcore blog\"}');

