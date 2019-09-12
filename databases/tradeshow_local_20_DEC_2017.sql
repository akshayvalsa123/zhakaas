-- MySQL dump 10.13  Distrib 5.7.20, for Linux (x86_64)
--
-- Host: localhost    Database: tradeshow
-- ------------------------------------------------------
-- Server version	5.7.20-0ubuntu0.16.04.1

/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8 */;
/*!40103 SET @OLD_TIME_ZONE=@@TIME_ZONE */;
/*!40103 SET TIME_ZONE='+00:00' */;
/*!40014 SET @OLD_UNIQUE_CHECKS=@@UNIQUE_CHECKS, UNIQUE_CHECKS=0 */;
/*!40014 SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0 */;
/*!40101 SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='NO_AUTO_VALUE_ON_ZERO' */;
/*!40111 SET @OLD_SQL_NOTES=@@SQL_NOTES, SQL_NOTES=0 */;

--
-- Table structure for table `Address`
--

DROP TABLE IF EXISTS `Address`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `Address` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `created` datetime DEFAULT NULL,
  `updated` datetime DEFAULT NULL,
  `address1` longtext NOT NULL,
  `address2` longtext,
  `street` varchar(100) DEFAULT NULL,
  `city` varchar(50) NOT NULL,
  `state` varchar(50) NOT NULL,
  `country` varchar(50) NOT NULL,
  `zipcode` varchar(20) NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=290 DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `Answer`
--

DROP TABLE IF EXISTS `Answer`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `Answer` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `answer` longtext,
  `lead_id` int(11) NOT NULL,
  `question_id` int(11) NOT NULL,
  PRIMARY KEY (`id`),
  KEY `Answer_8f635513` (`lead_id`),
  KEY `Answer_7aa0f6ee` (`question_id`),
  CONSTRAINT `Answer_lead_id_6345cbc24e0b9cb4_fk_Lead_id` FOREIGN KEY (`lead_id`) REFERENCES `Lead` (`id`),
  CONSTRAINT `Answer_question_id_52c30f9128e49abe_fk_QualifierQuestions_id` FOREIGN KEY (`question_id`) REFERENCES `QualifierQuestions` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=51011 DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `DeviceDetails`
--

DROP TABLE IF EXISTS `DeviceDetails`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `DeviceDetails` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `deviceName` varchar(300) NOT NULL,
  `deviceModel` varchar(100) NOT NULL,
  `appVersion` varchar(30) NOT NULL,
  `isActive` tinyint(1) NOT NULL,
  `initTime` datetime NOT NULL,
  `syncTime` datetime NOT NULL,
  `deviceID` varchar(100) NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=2 DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `Exhibitor`
--

DROP TABLE IF EXISTS `Exhibitor`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `Exhibitor` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `created` datetime DEFAULT NULL,
  `updated` datetime DEFAULT NULL,
  `name` varchar(100) NOT NULL,
  `email` varchar(254) NOT NULL,
  `contactNo` varchar(30) NOT NULL,
  `alternateEmail` varchar(254) DEFAULT NULL,
  `alternateContactNo` varchar(30) DEFAULT NULL,
  `licenseCount` int(11) NOT NULL,
  `address_id` int(11) NOT NULL,
  `tradeshow_id` int(11) NOT NULL,
  PRIMARY KEY (`id`),
  KEY `Exhibitor_address_id_3318e3a4688070ac_fk_Address_id` (`address_id`),
  KEY `Exhibitor_f85e1639` (`tradeshow_id`),
  CONSTRAINT `Exhibitor_address_id_3318e3a4688070ac_fk_Address_id` FOREIGN KEY (`address_id`) REFERENCES `Address` (`id`),
  CONSTRAINT `Exhibitor_tradeshow_id_1b1e938e8cd3d21d_fk_Tradeshow_id` FOREIGN KEY (`tradeshow_id`) REFERENCES `Tradeshow` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=174 DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `ExhibitorBooth`
--

DROP TABLE IF EXISTS `ExhibitorBooth`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `ExhibitorBooth` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `created` datetime DEFAULT NULL,
  `updated` datetime DEFAULT NULL,
  `name` varchar(100) NOT NULL,
  `email` varchar(254) NOT NULL,
  `contactNo` varchar(30) NOT NULL,
  `boothNo` varchar(30) DEFAULT NULL,
  `exhibitor_id` int(11) NOT NULL,
  `userName_id` int(11) NOT NULL,
  PRIMARY KEY (`id`),
  KEY `ExhibitorBooth_exhibitor_id_71b08965cd79ed7f_fk_Exhibitor_id` (`exhibitor_id`),
  KEY `ExhibitorBooth_8c6afa9c` (`userName_id`),
  CONSTRAINT `ExhibitorBooth_exhibitor_id_71b08965cd79ed7f_fk_Exhibitor_id` FOREIGN KEY (`exhibitor_id`) REFERENCES `Exhibitor` (`id`),
  CONSTRAINT `ExhibitorBooth_userName_id_c9c64f2eb706704_fk_UserLogin_id` FOREIGN KEY (`userName_id`) REFERENCES `UserLogin` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=205 DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `Fields`
--

DROP TABLE IF EXISTS `Fields`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `Fields` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `created` datetime DEFAULT NULL,
  `updated` datetime DEFAULT NULL,
  `name` varchar(100) NOT NULL,
  `description` longtext,
  `displayName` varchar(100) NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=11 DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `FieldsMapping`
--

DROP TABLE IF EXISTS `FieldsMapping`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `FieldsMapping` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `created` datetime DEFAULT NULL,
  `updated` datetime DEFAULT NULL,
  `fieldSeq` int(11) NOT NULL,
  `isUnique` tinyint(1) NOT NULL,
  `field_id` int(11) NOT NULL,
  `mapping_id` int(11) NOT NULL,
  PRIMARY KEY (`id`),
  KEY `FieldsMapping_field_id_30dee93e3b47fa4b_fk_Fields_id` (`field_id`),
  KEY `FieldsMapping_26fb0887` (`mapping_id`),
  CONSTRAINT `FieldsMapping_field_id_30dee93e3b47fa4b_fk_Fields_id` FOREIGN KEY (`field_id`) REFERENCES `Fields` (`id`),
  CONSTRAINT `FieldsMapping_mapping_id_4c38cefe7c69ff5f_fk_Mapping_id` FOREIGN KEY (`mapping_id`) REFERENCES `Mapping` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=379 DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `Industry`
--

DROP TABLE IF EXISTS `Industry`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `Industry` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `created` datetime DEFAULT NULL,
  `updated` datetime DEFAULT NULL,
  `name` varchar(100) NOT NULL,
  `description` longtext,
  PRIMARY KEY (`id`),
  UNIQUE KEY `name` (`name`)
) ENGINE=InnoDB AUTO_INCREMENT=33 DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `Lead`
--

DROP TABLE IF EXISTS `Lead`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `Lead` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `created` datetime DEFAULT NULL,
  `updated` datetime DEFAULT NULL,
  `exhibitorBooth_id` int(11) NOT NULL,
  `leadDetails_id` int(11) NOT NULL,
  `leadMaster_id` int(11) NOT NULL,
  PRIMARY KEY (`id`),
  KEY `Lead_b7935dc4` (`exhibitorBooth_id`),
  KEY `Lead_063063f9` (`leadDetails_id`),
  KEY `Lead_e57126fc` (`leadMaster_id`),
  CONSTRAINT `Lead_exhibitorBooth_id_1fdc664a68a4dcba_fk_ExhibitorBooth_id` FOREIGN KEY (`exhibitorBooth_id`) REFERENCES `ExhibitorBooth` (`id`),
  CONSTRAINT `Lead_leadDetails_id_10923a9ab202fb95_fk_LeadDetails_id` FOREIGN KEY (`leadDetails_id`) REFERENCES `LeadDetails` (`id`),
  CONSTRAINT `Lead_leadMaster_id_4c6b47aeea587382_fk_LeadMaster_id` FOREIGN KEY (`leadMaster_id`) REFERENCES `LeadMaster` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=5104 DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `LeadDetails`
--

DROP TABLE IF EXISTS `LeadDetails`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `LeadDetails` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `created` datetime DEFAULT NULL,
  `updated` datetime DEFAULT NULL,
  `scanType` varchar(100) NOT NULL,
  `syncID` varchar(100) NOT NULL,
  `captureTime` datetime NOT NULL,
  `lookupStatus` varchar(100) NOT NULL,
  `leadSyncStatus` varchar(100) NOT NULL,
  `leadType` varchar(100) NOT NULL,
  `device_id` int(11) DEFAULT NULL,
  `comment` longtext,
  `rating` int(11),
  PRIMARY KEY (`id`),
  KEY `LeadDetails_device_id_21fd7062a24a007d_fk_DeviceDetails_id` (`device_id`),
  CONSTRAINT `LeadDetails_device_id_21fd7062a24a007d_fk_DeviceDetails_id` FOREIGN KEY (`device_id`) REFERENCES `DeviceDetails` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=5104 DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `LeadFields`
--

DROP TABLE IF EXISTS `LeadFields`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `LeadFields` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `created` datetime DEFAULT NULL,
  `updated` datetime DEFAULT NULL,
  `fieldValue` longtext,
  `field_id` int(11) NOT NULL,
  `lead_id` int(11) NOT NULL,
  PRIMARY KEY (`id`),
  KEY `LeadFields_field_id_6d61b6e02d5aae84_fk_Fields_id` (`field_id`),
  KEY `LeadFields_8f635513` (`lead_id`),
  CONSTRAINT `LeadFields_field_id_6d61b6e02d5aae84_fk_Fields_id` FOREIGN KEY (`field_id`) REFERENCES `Fields` (`id`),
  CONSTRAINT `LeadFields_lead_id_730fe4ba5636fa59_fk_LeadMaster_id` FOREIGN KEY (`lead_id`) REFERENCES `LeadMaster` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=30523 DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `LeadMaster`
--

DROP TABLE IF EXISTS `LeadMaster`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `LeadMaster` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `created` datetime DEFAULT NULL,
  `updated` datetime DEFAULT NULL,
  `leadID` varchar(100) NOT NULL,
  `tradeshow_id` int(11) NOT NULL,
  PRIMARY KEY (`id`),
  KEY `LeadMaster_f85e1639` (`tradeshow_id`),
  CONSTRAINT `LeadMaster_tradeshow_id_48801546adbb6b3c_fk_Tradeshow_id` FOREIGN KEY (`tradeshow_id`) REFERENCES `Tradeshow` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=5092 DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `Mapping`
--

DROP TABLE IF EXISTS `Mapping`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `Mapping` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `created` datetime DEFAULT NULL,
  `updated` datetime DEFAULT NULL,
  `totalFields` int(11) NOT NULL,
  `badgeIDFieldSeq` int(11) NOT NULL,
  `badgeDataFieldSeq` int(11) NOT NULL,
  `tradeshow_id` int(11) NOT NULL,
  PRIMARY KEY (`id`),
  KEY `Mapping_f85e1639` (`tradeshow_id`),
  CONSTRAINT `Mapping_tradeshow_id_1d8c00921f7e66b5_fk_Tradeshow_id` FOREIGN KEY (`tradeshow_id`) REFERENCES `Tradeshow` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=67 DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `Qualifier`
--

DROP TABLE IF EXISTS `Qualifier`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `Qualifier` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `created` datetime DEFAULT NULL,
  `updated` datetime DEFAULT NULL,
  `qualifierName` varchar(300) NOT NULL,
  `screenNo` int(11) NOT NULL,
  `ansFormat` int(11) NOT NULL,
  `totalQuestions` int(11) NOT NULL,
  `exhibitor_id` int(11) NOT NULL,
  `qualifierTypeID_id` int(11) NOT NULL,
  PRIMARY KEY (`id`),
  KEY `Qualifier_exhibitor_id_70ea9804202a426_fk_Exhibitor_id` (`exhibitor_id`),
  KEY `Qualifier_c37bd1ac` (`qualifierTypeID_id`),
  CONSTRAINT `Qualifie_qualifierTypeID_id_7fbbc7706699230d_fk_QualifierType_id` FOREIGN KEY (`qualifierTypeID_id`) REFERENCES `QualifierType` (`id`),
  CONSTRAINT `Qualifier_exhibitor_id_70ea9804202a426_fk_Exhibitor_id` FOREIGN KEY (`exhibitor_id`) REFERENCES `Exhibitor` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=165 DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `QualifierQuestions`
--

DROP TABLE IF EXISTS `QualifierQuestions`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `QualifierQuestions` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `created` datetime DEFAULT NULL,
  `updated` datetime DEFAULT NULL,
  `seq` int(11) NOT NULL,
  `qualifier_id` int(11) NOT NULL,
  `question_id` int(11) NOT NULL,
  `mapping` varchar(500),
  PRIMARY KEY (`id`),
  KEY `QualifierQuestions_qualifier_id_512bed682fae8a9e_fk_Qualifier_id` (`qualifier_id`),
  KEY `QualifierQuestions_7aa0f6ee` (`question_id`),
  CONSTRAINT `QualifierQuestions_qualifier_id_512bed682fae8a9e_fk_Qualifier_id` FOREIGN KEY (`qualifier_id`) REFERENCES `Qualifier` (`id`),
  CONSTRAINT `QualifierQuestions_question_id_38f5a1fcc51320d7_fk_Question_id` FOREIGN KEY (`question_id`) REFERENCES `Question` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=518 DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `QualifierType`
--

DROP TABLE IF EXISTS `QualifierType`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `QualifierType` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `created` datetime DEFAULT NULL,
  `updated` datetime DEFAULT NULL,
  `qualifierType` varchar(100) NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=3 DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `Question`
--

DROP TABLE IF EXISTS `Question`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `Question` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `created` datetime DEFAULT NULL,
  `updated` datetime DEFAULT NULL,
  `question` longtext NOT NULL,
  `widgetName` varchar(100) NOT NULL,
  `options` varchar(300) NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=174 DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `ReportUrls`
--

DROP TABLE IF EXISTS `ReportUrls`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `ReportUrls` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `created` datetime(6) DEFAULT NULL,
  `updated` datetime(6) DEFAULT NULL,
  `name` varchar(500) NOT NULL,
  `url` longtext NOT NULL,
  `description` longtext,
  `seq` int(11) DEFAULT NULL,
  `tradeshow_id` int(11) NOT NULL,
  PRIMARY KEY (`id`),
  KEY `ReportUrls_tradeshow_id_48d269c081071d70_fk_Tradeshow_id` (`tradeshow_id`),
  CONSTRAINT `ReportUrls_tradeshow_id_48d269c081071d70_fk_Tradeshow_id` FOREIGN KEY (`tradeshow_id`) REFERENCES `Tradeshow` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=12 DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `Settings`
--

DROP TABLE IF EXISTS `Settings`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `Settings` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `settingType` varchar(100) NOT NULL,
  `settingName` varchar(100) NOT NULL,
  `created` datetime DEFAULT NULL,
  `updated` datetime DEFAULT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=8 DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `Sponsor`
--

DROP TABLE IF EXISTS `Sponsor`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `Sponsor` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `created` datetime DEFAULT NULL,
  `updated` datetime DEFAULT NULL,
  `name` varchar(100) NOT NULL,
  `description` longtext,
  PRIMARY KEY (`id`),
  UNIQUE KEY `name` (`name`)
) ENGINE=InnoDB AUTO_INCREMENT=8 DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `Tradeshow`
--

DROP TABLE IF EXISTS `Tradeshow`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `Tradeshow` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `created` datetime DEFAULT NULL,
  `updated` datetime DEFAULT NULL,
  `name` varchar(100) NOT NULL,
  `nameCode` varchar(10) DEFAULT NULL,
  `startDate` datetime NOT NULL,
  `endDate` datetime NOT NULL,
  `email` varchar(254) DEFAULT NULL,
  `contactNo` varchar(30) NOT NULL,
  `adminPassword` varchar(100) NOT NULL,
  `supportMessage` longtext,
  `website` varchar(300) DEFAULT NULL,
  `timeZone` varchar(30) DEFAULT NULL,
  `address_id` int(11) NOT NULL,
  `industry_id` int(11) DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `Tradeshow_address_id_9f30d93b59468b_fk_Address_id` (`address_id`),
  KEY `Tradeshow_industry_id_7dc7db6346a7eee0_fk_Industry_id` (`industry_id`),
  CONSTRAINT `Tradeshow_address_id_9f30d93b59468b_fk_Address_id` FOREIGN KEY (`address_id`) REFERENCES `Address` (`id`),
  CONSTRAINT `Tradeshow_industry_id_7dc7db6346a7eee0_fk_Industry_id` FOREIGN KEY (`industry_id`) REFERENCES `Industry` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=70 DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `TradeshowSettings`
--

DROP TABLE IF EXISTS `TradeshowSettings`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `TradeshowSettings` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `created` datetime DEFAULT NULL,
  `updated` datetime DEFAULT NULL,
  `settingValue` longtext NOT NULL,
  `defaultSettingValue` varchar(100) DEFAULT NULL,
  `setting_id` int(11) NOT NULL,
  `tradeshow_id` int(11) NOT NULL,
  PRIMARY KEY (`id`),
  KEY `TradeshowSettings_60190d67` (`setting_id`),
  KEY `TradeshowSettings_f85e1639` (`tradeshow_id`),
  CONSTRAINT `TradeshowSettings_setting_id_2a43a4f402df691a_fk_Settings_id` FOREIGN KEY (`setting_id`) REFERENCES `Settings` (`id`),
  CONSTRAINT `TradeshowSettings_tradeshow_id_43eac4661d454369_fk_Tradeshow_id` FOREIGN KEY (`tradeshow_id`) REFERENCES `Tradeshow` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=284 DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `Tradeshow_sponsors`
--

DROP TABLE IF EXISTS `Tradeshow_sponsors`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `Tradeshow_sponsors` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `tradeshow_id` int(11) NOT NULL,
  `sponsor_id` int(11) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `tradeshow_id` (`tradeshow_id`,`sponsor_id`),
  KEY `Tradeshow_sponsors_sponsor_id_305123a326443588_fk_Sponsor_id` (`sponsor_id`),
  CONSTRAINT `Tradeshow_sponsors_sponsor_id_305123a326443588_fk_Sponsor_id` FOREIGN KEY (`sponsor_id`) REFERENCES `Sponsor` (`id`),
  CONSTRAINT `Tradeshow_sponsors_tradeshow_id_67cf6555920f19f9_fk_Tradeshow_id` FOREIGN KEY (`tradeshow_id`) REFERENCES `Tradeshow` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=5 DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `UserLogin`
--

DROP TABLE IF EXISTS `UserLogin`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `UserLogin` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `created` datetime DEFAULT NULL,
  `updated` datetime DEFAULT NULL,
  `userName` varchar(100) NOT NULL,
  `password` varchar(100) NOT NULL,
  `isActive` tinyint(1) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `userName` (`userName`)
) ENGINE=InnoDB AUTO_INCREMENT=240 DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `UserLoginSession`
--

DROP TABLE IF EXISTS `UserLoginSession`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `UserLoginSession` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `created` datetime(6) DEFAULT NULL,
  `updated` datetime(6) DEFAULT NULL,
  `authToken` varchar(250) NOT NULL,
  `loginTime` datetime(6) NOT NULL,
  `logoutTime` datetime(6) DEFAULT NULL,
  `user_id` int(11) NOT NULL,
  `comment` varchar(500),
  `specialLogin` tinyint(1) NOT NULL,
  PRIMARY KEY (`id`),
  KEY `UserLoginSession_user_id_48e21acf6cffb16b_fk_UserLogin_id` (`user_id`),
  CONSTRAINT `UserLoginSession_user_id_48e21acf6cffb16b_fk_UserLogin_id` FOREIGN KEY (`user_id`) REFERENCES `UserLogin` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=7 DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `auth_group`
--

DROP TABLE IF EXISTS `auth_group`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `auth_group` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `name` varchar(80) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `name` (`name`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `auth_group_permissions`
--

DROP TABLE IF EXISTS `auth_group_permissions`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `auth_group_permissions` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `group_id` int(11) NOT NULL,
  `permission_id` int(11) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `group_id` (`group_id`,`permission_id`),
  KEY `auth_group__permission_id_1f49ccbbdc69d2fc_fk_auth_permission_id` (`permission_id`),
  CONSTRAINT `auth_group__permission_id_1f49ccbbdc69d2fc_fk_auth_permission_id` FOREIGN KEY (`permission_id`) REFERENCES `auth_permission` (`id`),
  CONSTRAINT `auth_group_permission_group_id_689710a9a73b7457_fk_auth_group_id` FOREIGN KEY (`group_id`) REFERENCES `auth_group` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `auth_permission`
--

DROP TABLE IF EXISTS `auth_permission`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `auth_permission` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `name` varchar(255) DEFAULT NULL,
  `content_type_id` int(11) NOT NULL,
  `codename` varchar(100) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `content_type_id` (`content_type_id`,`codename`),
  CONSTRAINT `auth__content_type_id_508cf46651277a81_fk_django_content_type_id` FOREIGN KEY (`content_type_id`) REFERENCES `django_content_type` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=97 DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `auth_user`
--

DROP TABLE IF EXISTS `auth_user`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `auth_user` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `password` varchar(128) NOT NULL,
  `last_login` datetime DEFAULT NULL,
  `is_superuser` tinyint(1) NOT NULL,
  `username` varchar(30) NOT NULL,
  `first_name` varchar(30) NOT NULL,
  `last_name` varchar(30) NOT NULL,
  `email` varchar(254) DEFAULT NULL,
  `is_staff` tinyint(1) NOT NULL,
  `is_active` tinyint(1) NOT NULL,
  `date_joined` datetime NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `username` (`username`)
) ENGINE=InnoDB AUTO_INCREMENT=2 DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `auth_user_groups`
--

DROP TABLE IF EXISTS `auth_user_groups`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `auth_user_groups` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `user_id` int(11) NOT NULL,
  `group_id` int(11) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `user_id` (`user_id`,`group_id`),
  KEY `auth_user_groups_group_id_33ac548dcf5f8e37_fk_auth_group_id` (`group_id`),
  CONSTRAINT `auth_user_groups_group_id_33ac548dcf5f8e37_fk_auth_group_id` FOREIGN KEY (`group_id`) REFERENCES `auth_group` (`id`),
  CONSTRAINT `auth_user_groups_user_id_4b5ed4ffdb8fd9b0_fk_auth_user_id` FOREIGN KEY (`user_id`) REFERENCES `auth_user` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `auth_user_user_permissions`
--

DROP TABLE IF EXISTS `auth_user_user_permissions`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `auth_user_user_permissions` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `user_id` int(11) NOT NULL,
  `permission_id` int(11) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `user_id` (`user_id`,`permission_id`),
  KEY `auth_user_u_permission_id_384b62483d7071f0_fk_auth_permission_id` (`permission_id`),
  CONSTRAINT `auth_user_u_permission_id_384b62483d7071f0_fk_auth_permission_id` FOREIGN KEY (`permission_id`) REFERENCES `auth_permission` (`id`),
  CONSTRAINT `auth_user_user_permissi_user_id_7f0938558328534a_fk_auth_user_id` FOREIGN KEY (`user_id`) REFERENCES `auth_user` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `django_admin_log`
--

DROP TABLE IF EXISTS `django_admin_log`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `django_admin_log` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `action_time` datetime NOT NULL,
  `object_id` longtext,
  `object_repr` varchar(200) NOT NULL,
  `action_flag` smallint(5) unsigned NOT NULL,
  `change_message` longtext NOT NULL,
  `content_type_id` int(11) DEFAULT NULL,
  `user_id` int(11) NOT NULL,
  PRIMARY KEY (`id`),
  KEY `djang_content_type_id_697914295151027a_fk_django_content_type_id` (`content_type_id`),
  KEY `django_admin_log_user_id_52fdd58701c5f563_fk_auth_user_id` (`user_id`),
  CONSTRAINT `djang_content_type_id_697914295151027a_fk_django_content_type_id` FOREIGN KEY (`content_type_id`) REFERENCES `django_content_type` (`id`),
  CONSTRAINT `django_admin_log_user_id_52fdd58701c5f563_fk_auth_user_id` FOREIGN KEY (`user_id`) REFERENCES `auth_user` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=266 DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `django_content_type`
--

DROP TABLE IF EXISTS `django_content_type`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `django_content_type` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `app_label` varchar(100) NOT NULL,
  `model` varchar(100) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `django_content_type_app_label_45f3b1d93ec8c61c_uniq` (`app_label`,`model`)
) ENGINE=InnoDB AUTO_INCREMENT=33 DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `django_migrations`
--

DROP TABLE IF EXISTS `django_migrations`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `django_migrations` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `app` varchar(255) NOT NULL,
  `name` varchar(255) NOT NULL,
  `applied` datetime NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=31 DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `django_session`
--

DROP TABLE IF EXISTS `django_session`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `django_session` (
  `session_key` varchar(40) NOT NULL,
  `session_data` longtext NOT NULL,
  `expire_date` datetime NOT NULL,
  PRIMARY KEY (`session_key`),
  KEY `django_session_de54fa62` (`expire_date`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;
/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;

-- Dump completed on 2017-12-20 16:21:12
