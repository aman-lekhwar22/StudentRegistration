CREATE DATABASE StudentDB;


 USE StudentDB;


CREATE TABLE Students (
    StudentID INT IDENTITY(1,1) PRIMARY KEY,
    Name VARCHAR(100) NOT NULL,
    Age INT NOT NULL,
    Percentage DECIMAL(5,2) NOT NULL,
    Stream VARCHAR(50) NOT NULL,
    Grade VARCHAR(5)
);

INSERT INTO Students (Name, Age, Percentage, Stream, Grade)
VALUES ('Rahul', 20, 85.50, 'Science', 'A');


SELECT * FROM Students;