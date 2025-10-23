-- ==========================================
-- AI有声书工具 - 数据库初始化脚本
-- ==========================================

-- 设置字符集
SET NAMES utf8mb4;
SET FOREIGN_KEY_CHECKS = 0;

-- ==========================================
-- 项目表
-- ==========================================
CREATE TABLE IF NOT EXISTS `projects` (
  `id` INT AUTO_INCREMENT PRIMARY KEY,
  `name` VARCHAR(255) NOT NULL COMMENT '项目名称',
  `description` TEXT COMMENT '项目描述',
  `cover_image` VARCHAR(512) COMMENT '封面图片URL',
  `status` VARCHAR(50) DEFAULT 'draft' COMMENT '状态: draft, processing, completed, failed',
  `chapters_count` INT DEFAULT 0 COMMENT '章节数量',
  `characters_count` INT DEFAULT 0 COMMENT '角色数量',
  `total_duration` FLOAT DEFAULT 0 COMMENT '总时长（秒）',
  `created_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  `updated_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  INDEX `idx_status` (`status`),
  INDEX `idx_created_at` (`created_at`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='项目表';

-- ==========================================
-- 章节表
-- ==========================================
CREATE TABLE IF NOT EXISTS `chapters` (
  `id` INT AUTO_INCREMENT PRIMARY KEY,
  `project_id` INT NOT NULL COMMENT '所属项目ID',
  `title` VARCHAR(255) NOT NULL COMMENT '章节标题',
  `order_index` INT NOT NULL DEFAULT 0 COMMENT '排序序号',
  `content` LONGTEXT COMMENT '原始文本内容',
  `word_count` INT DEFAULT 0 COMMENT '字数',
  `status` VARCHAR(50) DEFAULT 'pending' COMMENT '状态: pending, processing, completed, failed',
  `duration` FLOAT DEFAULT 0 COMMENT '音频时长（秒）',
  `created_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  `updated_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  FOREIGN KEY (`project_id`) REFERENCES `projects`(`id`) ON DELETE CASCADE,
  INDEX `idx_project_id` (`project_id`),
  INDEX `idx_order_index` (`order_index`),
  INDEX `idx_status` (`status`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='章节表';

-- ==========================================
-- 角色表
-- ==========================================
CREATE TABLE IF NOT EXISTS `characters` (
  `id` INT AUTO_INCREMENT PRIMARY KEY,
  `project_id` INT NOT NULL COMMENT '所属项目ID',
  `name` VARCHAR(255) NOT NULL COMMENT '角色名称',
  `avatar` VARCHAR(512) COMMENT '头像URL',
  `description` TEXT COMMENT '角色描述',
  `dialogue_count` INT DEFAULT 0 COMMENT '对话数量',
  `total_duration` FLOAT DEFAULT 0 COMMENT '总时长（秒）',
  `voice_config` JSON COMMENT '声音配置: {engine, voice_id, speed, pitch, volume}',
  `created_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  `updated_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  FOREIGN KEY (`project_id`) REFERENCES `projects`(`id`) ON DELETE CASCADE,
  INDEX `idx_project_id` (`project_id`),
  INDEX `idx_name` (`name`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='角色表';

-- ==========================================
-- 对话/旁白表
-- ==========================================
CREATE TABLE IF NOT EXISTS `dialogues` (
  `id` INT AUTO_INCREMENT PRIMARY KEY,
  `chapter_id` INT NOT NULL COMMENT '所属章节ID',
  `order_index` INT NOT NULL DEFAULT 0 COMMENT '排序序号',
  `type` VARCHAR(50) NOT NULL DEFAULT 'dialogue' COMMENT '类型: dialogue, narration',
  `content` TEXT NOT NULL COMMENT '对话内容',
  `character_id` INT COMMENT '角色ID（旁白时为NULL）',
  `start_time` FLOAT COMMENT '开始时间（秒）',
  `end_time` FLOAT COMMENT '结束时间（秒）',
  `audio_path` VARCHAR(512) COMMENT '音频文件路径',
  `status` VARCHAR(50) DEFAULT 'pending' COMMENT '状态: pending, generating, generated, failed',
  `voice_config` JSON COMMENT '独立声音配置（可选）',
  `pause_after` FLOAT DEFAULT 0.5 COMMENT '段落后停顿时长（秒）',
  `created_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  `updated_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  FOREIGN KEY (`chapter_id`) REFERENCES `chapters`(`id`) ON DELETE CASCADE,
  FOREIGN KEY (`character_id`) REFERENCES `characters`(`id`) ON DELETE SET NULL,
  INDEX `idx_chapter_id` (`chapter_id`),
  INDEX `idx_character_id` (`character_id`),
  INDEX `idx_order_index` (`order_index`),
  INDEX `idx_status` (`status`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='对话旁白表';

-- ==========================================
-- 导出记录表
-- ==========================================
CREATE TABLE IF NOT EXISTS `audio_exports` (
  `id` INT AUTO_INCREMENT PRIMARY KEY,
  `project_id` INT NOT NULL COMMENT '所属项目ID',
  `format` VARCHAR(50) NOT NULL COMMENT '音频格式: mp3, wav, m4a, ogg',
  `quality` VARCHAR(50) NOT NULL COMMENT '音质: standard, high, ultra',
  `file_path` VARCHAR(512) NOT NULL COMMENT '文件路径',
  `file_size` BIGINT DEFAULT 0 COMMENT '文件大小（字节）',
  `export_range` JSON COMMENT '导出范围配置',
  `created_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  FOREIGN KEY (`project_id`) REFERENCES `projects`(`id`) ON DELETE CASCADE,
  INDEX `idx_project_id` (`project_id`),
  INDEX `idx_created_at` (`created_at`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='导出记录表';

-- ==========================================
-- 插入示例数据（可选）
-- ==========================================

-- 示例项目
INSERT INTO `projects` (`name`, `description`, `status`, `chapters_count`, `characters_count`)
VALUES 
('示例小说项目', '这是一个示例项目，用于演示系统功能', 'draft', 0, 0)
ON DUPLICATE KEY UPDATE `name` = `name`;

-- 重置外键检查
SET FOREIGN_KEY_CHECKS = 1;

-- 显示创建的表
SHOW TABLES;

