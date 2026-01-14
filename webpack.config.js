const path = require("path");
const TerserPlugin = require("terser-webpack-plugin");
const CopyPlugin = require("copy-webpack-plugin");

const webpackConfig = (environment, argv) => {
    const isProduction = argv.mode === "production";

    const config = {
        entry: {
            main: "./src/scripts/main.js",
            analytics: "./src/scripts/analytics.js",
        },
        mode: isProduction ? "production" : "development",
        resolve: {
            extensions: [".js", ".mjs"],
        },
        module: {
            rules: [
                {
                    test: /\.m?js$/,
                    exclude: /(node_modules|bower_components)/,
                    use: {
                        loader: "babel-loader",
                        options: {
                            presets: ["@babel/preset-env"],
                        },
                    },
                },
                {
                    // Handles fonts referenced in CSS
                    test: /\.(woff|woff2)$/,
                    include: path.resolve(__dirname, "src/images/"),
                    type: "asset/resource",
                    generator: {
                        filename: "assets/fonts/[name][ext]",
                    },
                },
                {
                    // Handles CSS background images
                    test: /\.(svg|jpg|png|gif|webp)$/,
                    include: path.resolve(__dirname, "src/images/cssBackgrounds/"),
                    type: "asset",
                    parser: {
                        dataUrlCondition: {
                            maxSize: 1024,
                        },
                    },
                    generator: {
                        filename: "assets/images/cssBackgrounds/[name][ext]",
                    },
                },
            ],
        },
        plugins: [
            new CopyPlugin({
                patterns: [
                    {
                        // Copy images (excluding CSS backgrounds which are handled above)
                        from: "images",
                        context: path.resolve(__dirname, "src/"),
                        to: path.resolve(__dirname, "app/static/assets/images"),
                        globOptions: {
                            ignore: ["**/cssBackgrounds/**"],
                        },
                        noErrorOnMissing: true,
                    },
                ],
            }),
        ],
        output: {
            path: path.resolve(__dirname, "app/static"),
            filename: "[name].min.js",
            clean: false, // Don't clean CSS files
        },
        optimization: {
            minimize: isProduction,
            minimizer: [
                new TerserPlugin({
                    extractComments: false,
                }),
            ],
        },
        devtool: isProduction ? "source-map" : "inline-source-map",
    };

    if (!isProduction) {
        const stats = {
            builtAt: false,
            chunks: false,
            hash: false,
            colors: true,
            reasons: false,
            version: false,
            modules: false,
            performance: false,
            children: false,
            assets: false,
        };
        config.stats = stats;
    }

    return config;
};

module.exports = webpackConfig;
