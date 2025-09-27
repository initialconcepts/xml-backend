import express from 'express';
import multer from 'multer';
import cors from 'cors';
import xml2js from 'xml2js';

const app = express();
app.use(cors({ origin: "*" }));
app.use(express.json());

const storage = multer.memoryStorage();
const upload = multer({ storage });

app.get('/preview', (req, res) => {
  res.json({ message: "hello from backend" });
});

app.post('/upload-event', upload.single('xmlFile'), async (req, res) => {
  console.log("🔹 File Received");
  try {
    if (!req.file) return res.json({ success: true, stats: null });

    const xmlContent = req.file.buffer.toString('utf-8');
    console.log("🔹 Full XML content received:\n", xmlContent);

    const parser = new xml2js.Parser();
    let parsedData;
    try {
      parsedData = await parser.parseStringPromise(xmlContent);
      console.log("🔹 Parsed XML JSON:\n", JSON.stringify(parsedData, null, 2));
    } catch (err) {
      console.error("❌ XML parsing error:", err);
      return res.json({ success: false, error: "Invalid XML format" });
    }

    let teams = parsedData?.bsgame?.team || [];
    let stats = {};

    teams.forEach(team => {
      const name = team.$?.name || "Unknown Team";
      const totals = team.totals?.[0] || {};

      const hitting = totals.hitting?.[0]?.$ || {};
      const fielding = totals.fielding?.[0]?.$ || {};
      const hsitsummary = totals.hsitsummary?.[0]?.$ || {};

      stats[name] = {
        AB: Number(hitting.ab || 0),
        R: Number(hitting.r || 0),
        H: Number(hitting.h || 0),
        RBI: Number(hitting.rbi || 0),
        BB: Number(hitting.bb || 0),
        SO: Number(hitting.so || 0),
        SB: Number(hitting.sb || 0),
        E: Number(fielding.e || 0),
        LOB: Number(hsitsummary.lob || 0)
      };
    });

    console.log("🔹 Final stats object to return:\n", stats);
    res.json({ success: true, stats });
  } catch (err) {
    console.error(err);
    res.status(500).json({ success: false, error: 'Server error' });
  }
});

const PORT = process.env.PORT || 3000;
app.listen(PORT, () => console.log(`Server running on port ${PORT}`));
