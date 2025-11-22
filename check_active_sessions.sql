-- Check active user sessions
-- Shows who is currently logged in and when they last authenticated

SELECT 
    username,
    email,
    last_login,
    created_at,
    TIMESTAMPDIFF(MINUTE, last_login, NOW()) as minutes_since_last_login
FROM users
WHERE last_login IS NOT NULL
ORDER BY last_login DESC;

-- To see very recent activity (last 5 minutes):
SELECT 
    username,
    email,
    last_login,
    TIMESTAMPDIFF(MINUTE, last_login, NOW()) as minutes_ago
FROM users
WHERE last_login >= DATE_SUB(NOW(), INTERVAL 5 MINUTE)
ORDER BY last_login DESC;

-- To check if anyone is likely active (last 30 minutes):
SELECT 
    COUNT(*) as active_users
FROM users
WHERE last_login >= DATE_SUB(NOW(), INTERVAL 30 MINUTE);
