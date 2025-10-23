#!/usr/bin/env python3
"""Setup script to create the database and table for news scraping."""

import sys
import pymysql
from config import DB_CONFIG


def setup_database():
    try:
        connection_config = DB_CONFIG.copy()
        database_name = connection_config.pop('database')
        
        connection = pymysql.connect(**connection_config)
        cursor = connection.cursor()
        
        print(f"Creating database: {database_name}")
        cursor.execute(
            f"CREATE DATABASE IF NOT EXISTS {database_name} "
            "DEFAULT CHARACTER SET utf8mb4 DEFAULT COLLATE utf8mb4_unicode_ci"
        )
        connection.commit()
        
        cursor.execute(f"USE {database_name}")
        
        print(f"Creating table: news_articles")
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS news_articles (
              id INT UNSIGNED NOT NULL AUTO_INCREMENT,
              title VARCHAR(512) NOT NULL,
              url VARCHAR(512) NOT NULL,
              content LONGTEXT NOT NULL,
              created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
              updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
              PRIMARY KEY (id),
              UNIQUE KEY uniq_news_articles_url (url)
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
        """)
        connection.commit()
        
        cursor.close()
        connection.close()
        
        print(f"✓ Database and table created successfully")
        return True
        
    except Exception as e:
        print(f"✗ Failed to setup database: {e}")
        return False


if __name__ == "__main__":
    success = setup_database()
    sys.exit(0 if success else 1)
