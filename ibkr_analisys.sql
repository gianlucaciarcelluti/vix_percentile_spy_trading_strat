SELECT
    SUM(COALESCE(realized_pl, 0) + COALESCE(mtm_pl, 0)) AS total_pl,
    SUM(COALESCE(comm_fee, 0)) AS total_commissions,
    SUM(COALESCE(realized_pl, 0) + COALESCE(mtm_pl, 0) + COALESCE(comm_fee, 0)) AS total_pl_minus_commissions
FROM
    ibkr_trades
WHERE
    datetime >= '2025-01-01';

SELECT
    -- Estrae il sottostante: per le opzioni prende solo la prima parte di symbol (prima di spazio o primo carattere non alfa), altrimenti usa symbol
    COALESCE(
        NULLIF(option_underlying, ''),
        REGEXP_REPLACE(symbol, '[^A-Z0-9].*$', '')
    ) AS underlying,
    SUM(COALESCE(realized_pl, 0) + COALESCE(mtm_pl, 0)) AS total_pl,
    SUM(COALESCE(comm_fee, 0)) AS total_commissions,
    SUM(COALESCE(realized_pl, 0) + COALESCE(mtm_pl, 0) + COALESCE(comm_fee, 0)) AS total_pl_minus_commissions
FROM
    ibkr_trades
WHERE
    datetime >= '2025-01-01'
GROUP BY
    COALESCE(
        NULLIF(option_underlying, ''),
        REGEXP_REPLACE(symbol, '[^A-Z0-9].*$', '')
    )
ORDER BY
    total_pl_minus_commissions DESC;