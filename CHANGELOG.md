History
-------

**2022-04-04 (0.2.1)**
 - Add parameter separator to function range_conv

**2021-05-27 (0.2.0)**
 - Add overview table to API documentation
 - All parameters but 'string' are now keyword-only
 - Add functions sequence and range_conv
 - Rename functions: boolean -> bool_conv, datetime -> datetime_conv,
   date -> date_conv, time -> time_conv

**2021-01-25 (0.1.1)**
 - Bugfix: function duration now raises ValueError when hour, minute, or second
   are negative or when minute or second are > 59
 - Add parameter use_locale to function duration

**2021-01-22 (0.1.0)**
 - First public release
