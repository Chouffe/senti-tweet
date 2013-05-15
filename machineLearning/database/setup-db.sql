-- Create Table
CREATE TABLE sentiments
(Entry VARCHAR(255),
Negativ VARCHAR(255),
Active VARCHAR(255),
IAV VARCHAR(255),
Positiv VARCHAR(255),
Strong VARCHAR(255),
PowTot VARCHAR(255),
Ngtv VARCHAR(255),
Pstv VARCHAR(255),
Passive VARCHAR(255),
ComForm VARCHAR(255),
EnlTot VARCHAR(255),
Hostile VARCHAR(255),
HU VARCHAR(255),
Weak VARCHAR(255),
Virtue VARCHAR(255)
);

-- Import Values
\copy public.sentiments from 'lexicon.csv' delimiter ';';

-- Show structure of the table
-- describe table:
\d sentiments
