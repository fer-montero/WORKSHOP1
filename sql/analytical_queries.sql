USE recruitment_dw;


-- ============================================================
-- R1 — HIRING TRENDS
-- ============================================================
-- Pregunta de negocio:
-- ¿Cómo ha evolucionado la cantidad de contrataciones a lo
-- largo del tiempo?

SELECT
    d.year,
    d.month,
    COUNT(*) AS total_applications,
    SUM(f.hired_indicator) AS total_hired,
    ROUND(
        SUM(f.hired_indicator) * 100.0 / COUNT(*),
        2
    ) AS hiring_rate
FROM fact_application f
JOIN dim_date d
    ON f.date_key = d.date_key
GROUP BY
    d.year,
    d.month
ORDER BY
    d.year,
    d.month;


-- ============================================================
-- R2 — TECHNOLOGY ANALYSIS
-- ============================================================
-- Pregunta de negocio:
-- ¿Qué tecnologías presentan mayor demanda y mejores resultados
-- de contratación?

SELECT
    t.technology,
    COUNT(*) AS total_applications,
    SUM(f.hired_indicator) AS total_hired,
    ROUND(
        SUM(f.hired_indicator) * 100.0 / COUNT(*),
        2
    ) AS hiring_rate,
    ROUND(AVG(f.code_score), 2) AS avg_code_score,
    ROUND(AVG(f.interview_score), 2) AS avg_interview_score
FROM fact_application f
JOIN dim_technology t
    ON f.technology_key = t.technology_key
GROUP BY
    t.technology
ORDER BY
    total_applications DESC;


-- ============================================================
-- R3 — CANDIDATE PROFILE ANALYSIS
-- ============================================================
-- Pregunta de negocio:
-- ¿Qué perfiles de candidatos presentan mejores resultados
-- de contratación según su seniority y experiencia?

SELECT
    c.seniority,
    ROUND(AVG(c.yoe), 2) AS avg_years_experience,
    COUNT(*) AS total_applications,
    SUM(f.hired_indicator) AS total_hired,
    ROUND(
        SUM(f.hired_indicator) * 100.0 / COUNT(*),
        2
    ) AS hiring_rate,
    ROUND(AVG(f.code_score), 2) AS avg_code_score,
    ROUND(AVG(f.interview_score), 2) AS avg_interview_score
FROM fact_application f
JOIN dim_candidate c
    ON f.candidate_key = c.candidate_key
GROUP BY
    c.seniority
ORDER BY
    hiring_rate DESC;


-- ============================================================
-- R4 — MERCADOS DE RECLUTAMIENTO ATRACTIVOS
-- ============================================================
-- Pregunta de negocio:
-- ¿Qué países representan mercados de reclutamiento más
-- atractivos según el volumen de candidatos y su tasa de
-- contratación?

SELECT
    c.country,
    COUNT(*) AS total_applications,
    SUM(f.hired_indicator) AS total_hired,
    ROUND(
        SUM(f.hired_indicator) * 100.0 / COUNT(*),
        2
    ) AS hiring_rate
FROM fact_application f
JOIN dim_country c
    ON f.country_key = c.country_key
GROUP BY
    c.country
ORDER BY
    hiring_rate DESC,
    total_applications DESC;


-- ============================================================
-- R5 — TECNOLOGÍAS CON DIFICULTADES DE CONTRATACIÓN
-- ============================================================
-- Pregunta de negocio:
-- ¿Qué tecnologías presentan dificultades para convertir las
-- aplicaciones recibidas en contrataciones?

-- Se consideran únicamente tecnologías con al menos 50
-- aplicaciones para evitar conclusiones basadas en muestras
-- demasiado pequeñas.

SELECT
    t.technology,
    COUNT(*) AS total_applications,
    SUM(f.hired_indicator) AS total_hired,
    ROUND(
        SUM(f.hired_indicator) * 100.0 / COUNT(*),
        2
    ) AS hiring_rate,
    ROUND(AVG(f.code_score), 2) AS avg_code_score,
    ROUND(AVG(f.interview_score), 2) AS avg_interview_score
FROM fact_application f
JOIN dim_technology t
    ON f.technology_key = t.technology_key
GROUP BY
    t.technology
HAVING
    COUNT(*) >= 50
ORDER BY
    hiring_rate ASC,
    total_applications DESC;