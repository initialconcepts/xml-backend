const express = require("express");
const multer = require("multer");
const xml2js = require("xml2js");
const cors = require("cors");

const app = express();
app.use(cors());

const upload = multer({ storage: multer.memoryStorage() });

app.post("/upload-event", upload.single("xmlFile"), async (req, res) => {
  try {
    if (!req.file) return res.json({ success: false, error: "No file uploaded" });

    const xmlString = req.file.buffer.toString();
    const result = await xml2js.parseStringPromise(xmlString);

    const stats = {};
    if (result.stats) {
      for (const [key, value] of Object.entries(result.stats)) {
        stats[key] = parseFloat(value[0]) || 0;
      }
    }

    res.json({ success: true, stats });
  } catch (err) {
    console.error("XML parse error:", err);
    res.json({ success: false, error: "Failed to parse XML" });
  }
});

const PORT = process.env.PORT || 3000;
app.listen(PORT, () => console.log(`✅ Server running on port ${PORT}`));
