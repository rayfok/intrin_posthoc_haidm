const path = require("path");

module.exports = {
  entry: "./haidm/js/main.js",
  output: {
    path: path.join(__dirname, "/haidm/static/js/"),
    filename: "bundle.js",
  },
  module: {
    rules: [
      {
        loader: "babel-loader",
        exclude: /node_modules/,
        options: {
          presets: ["@babel/preset-env", "@babel/react"],
          plugins: ["@babel/plugin-proposal-class-properties"],
        },
      },
      {
        test: /\.css$/i,
        use: ["style-loader", "css-loader"],
      },
    ],
  },
  resolve: {
    extensions: [".js"],
  },
  mode: "production",
  performance: {
    hints: process.env.NODE_ENV === "production" ? "warning" : false,
  },
};
