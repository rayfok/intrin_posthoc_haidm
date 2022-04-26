const path = require("path");
const TerserPlugin = require("terser-webpack-plugin");

module.exports = {
  entry: "./static/js/main.js",
  output: {
    path: path.join(__dirname, "/static/dist/"),
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
  optimization: {
    minimizer: [
      new TerserPlugin({
        extractComments: false,
      }),
    ],
  },
  resolve: {
    extensions: [".js"],
  },
  performance: {
    hints: process.env.NODE_ENV === "production" ? "warning" : false,
  },
};
