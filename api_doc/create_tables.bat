@echo off
cd /d %~dp0

REM 交互式输入
set /p MYSQL_USER=请输入MySQL用户名（默认root）:
if "%MYSQL_USER%"=="" set MYSQL_USER=root

set /p MYSQL_PWD=请输入MySQL密码:
set /p DB_NAME=请输入要创建的数据库名（默认popquiz）:
if "%DB_NAME%"=="" set DB_NAME=popquiz

set SQL_FILE=create_tables.sql

echo 当前目录为：
cd

echo 检查SQL文件是否存在：
dir %SQL_FILE%

mysql -u%MYSQL_USER% -p%MYSQL_PWD% -e "CREATE DATABASE IF NOT EXISTS %DB_NAME% DEFAULT CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;"
echo 正在导入表结构 ...
mysql -u%MYSQL_USER% -p%MYSQL_PWD% %DB_NAME% < %SQL_FILE%

echo 操作完成！
pause