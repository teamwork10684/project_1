@echo off
cd /d %~dp0

REM ����ʽ����
set /p MYSQL_USER=������MySQL�û�����Ĭ��root��:
if "%MYSQL_USER%"=="" set MYSQL_USER=root

set /p MYSQL_PWD=������MySQL����:
set /p DB_NAME=������Ҫ���������ݿ�����Ĭ��popquiz��:
if "%DB_NAME%"=="" set DB_NAME=popquiz

set SQL_FILE=create_tables.sql

echo ��ǰĿ¼Ϊ��
cd

echo ���SQL�ļ��Ƿ���ڣ�
dir %SQL_FILE%

mysql -u%MYSQL_USER% -p%MYSQL_PWD% -e "CREATE DATABASE IF NOT EXISTS %DB_NAME% DEFAULT CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;"
echo ���ڵ����ṹ ...
mysql -u%MYSQL_USER% -p%MYSQL_PWD% %DB_NAME% < %SQL_FILE%

echo ������ɣ�
pause