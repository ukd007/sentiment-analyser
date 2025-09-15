//Requirements
const express = require("express");
const path = require("path");
const app = express();

//Express Configuration
app.set("view engine", "ejs");
app.set("views", path.join(__dirname, "views"));

const PORT = process.env.PORT || 8080;

// Middleware to serve static files (CSS, JS, images)
app.use(express.static(path.join(__dirname, "public")));

//Routes
app.get("/", (req, res) => {
  res.render("user/home");
});

app.get("/uploadComment", (req, res) => {
  res.render("user/uploadComment"); 
});


// Start server
app.listen(8080, () => {
  console.log(`🚀 Server running on http://localhost:${PORT}`);
});
