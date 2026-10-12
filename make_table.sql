-- 删除旧表（如果存在），避免重复创建报错
-- Если таблица vacancy уже существует, удаляем её
DROP TABLE IF EXISTS vacancy;

-- 创建数据表 vacancy，用来存放岗位原始数据
-- Создание таблицы vacancy для хранения исходных данных вакансий 
CREATE TABLE IF NOT EXISTS vacancy (
    id INT PRIMARY KEY,
    title TEXT,
    company TEXT,
    city_district TEXT,
    salary_min INT,
    salary_max INT,
    experience TEXT,
    description TEXT,
    published_at TEXT
);
