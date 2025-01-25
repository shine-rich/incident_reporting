const express = require('express');
const mysql = require('mysql2');

const app = express();
app.use(express.json());
const port = 3000;

app.listen(port, () => {
  console.log(`Server is running on port ${port}`);
});

const conn = mysql.createPool({
    connectionLimit: 10,
    host: '127.0.0.1',
    user: 'appuser',
    password: 'password',
    database: 'stardust'
});

// Create a new incident
app.post('/incidents', (req, res) => {
    const { name, email, incident_summary, incident_type } = req.body;
    conn.query(
        'INSERT INTO incidents (name, email, incident_summary, incident_type) VALUES (?, ?, ?, ?)',
        [name, email, incident_summary, incident_type || 'others'], // Default to 'others' if incident_type is not provided
        (err, result) => {
            if (err) throw err;
            res.send('incident added successfully');
        }
    );
});

// Get all incidents
app.get('/incidents', (req, res) => {
    conn.query('SELECT * FROM incidents', (err, rows) => {
        if (err) throw err;
        res.json(rows);
    });
});

// Get incident by ID
app.get('/incidents/:id', (req, res) => {
    const incidentReportId = req.params.id;
    conn.query('SELECT * FROM incidents WHERE id = ?', incidentReportId, (err, rows) => {
        if (err) throw err;
        res.json(rows[0]);
    });
});

// Update incident by ID
app.put('/incidents/:id', (req, res) => {
    const incidentReportId = req.params.id;
    const { name, email, incident_summary, incident_type } = req.body;
    conn.query(
        'UPDATE incidents SET name = ?, email = ?, incident_summary = ?, incident_type = ? WHERE id = ?',
        [name, email, incident_summary, incident_type || 'others', incidentReportId], // Default to 'others' if incident_type is not provided
        (err, result) => {
            if (err) throw err;
            res.send('Incident report updated successfully');
        }
    );
});

// Delete incident by ID
app.delete('/incidents/:id', (req, res) => {
    const incidentReportId = req.params.id;
    conn.query('DELETE FROM incidents WHERE id = ?', incidentReportId, (err, result) => {
        if (err) throw err;
        res.send('incident deleted successfully');
    });
});
