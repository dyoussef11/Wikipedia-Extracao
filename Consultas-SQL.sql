-- Selecionar a quantidade de sítios agrupados por tipo em uma região específica

SELECT r.name, s.type_name, sum(h.site_count) AS soma
FROM site_types s join heritage_sites_counts h ON h.site_type_id=s.id_site_types
JOIN countries c ON c.id_countries=h.country_id 
JOIN regions r ON c.region_id=r.id_regions
GROUP BY s.type_name, r.name


-- Mostre o total de sítios por país

SELECT c.name, sum(h.site_count) AS numero_de_sitios
FROM countries c JOIN heritage_sites_counts h ON c.id_countries=h.country_id
GROUP BY c.name


-- Mostre os países europeus com mais de 10 sítios, ordene em ordem decrescente

SELECT c.name, h.site_count
FROM regions r JOIN countries c ON c.region_id=r.id_regions 
JOIN heritage_sites_counts h ON c.id_countries=h.country_id
WHERE r.name like '%Europe%'
AND h.site_count > 10
ORDER BY h.site_count DESC

-- Mostre os países que não possuem sítios mistos

SELECT DISTINCT c.name
FROM countries c JOIN heritage_sites_counts h ON c.id_countries=h.country_id
WHERE h.country_id NOT IN(SELECT  h.country_id FROM heritage_sites_counts h JOIN site_types s ON s.id_site_types=h.site_type_id
							WHERE type_name='Mixed' and site_count = 0)

							
-- Mostre as regiões que concentram mais sítios
							
SELECT r.name, SUM(h.site_count) as soma_de_sitios
FROM regions r JOIN countries c ON c.region_id=r.id_regions  
JOIN heritage_sites_counts h ON c.id_countries=h.country_id
GROUP BY 1
ORDER BY 2 DESC



