USE recruitment_dw;

DROP TABLE IF EXISTS fact_application;
DROP TABLE IF EXISTS dim_date;
DROP TABLE IF EXISTS dim_candidate;
DROP TABLE IF EXISTS dim_technology;
DROP TABLE IF EXISTS dim_country;

CREATE TABLE dim_date (
    date_key    INT PRIMARY KEY,
    day         INT NOT NULL,
    month       INT NOT NULL,
    quarter     INT NOT NULL,
    year        INT NOT NULL
);

CREATE TABLE dim_candidate (
    candidate_key INT PRIMARY KEY,
    first_name    VARCHAR(100),
    last_name     VARCHAR(100),
    email         VARCHAR(150),
    yoe           INT,
    seniority     VARCHAR(50)
);

CREATE TABLE dim_technology (
    technology_key INT PRIMARY KEY,
    technology      VARCHAR(100) NOT NULL
);

CREATE TABLE dim_country (
    country_key INT PRIMARY KEY,
    country     VARCHAR(100) NOT NULL
);

CREATE TABLE fact_application (
    application_key   INT PRIMARY KEY,
    date_key          INT NOT NULL,
    candidate_key     INT NOT NULL,
    technology_key    INT NOT NULL,
    country_key       INT NOT NULL,
    code_score        DECIMAL(4,2),
    interview_score   DECIMAL(4,2),
    hired_indicator   TINYINT,
    CONSTRAINT fk_fact_date        FOREIGN KEY (date_key)       REFERENCES dim_date(date_key),
    CONSTRAINT fk_fact_candidate   FOREIGN KEY (candidate_key)  REFERENCES dim_candidate(candidate_key),
    CONSTRAINT fk_fact_technology  FOREIGN KEY (technology_key) REFERENCES dim_technology(technology_key),
    CONSTRAINT fk_fact_country     FOREIGN KEY (country_key)    REFERENCES dim_country(country_key)
);