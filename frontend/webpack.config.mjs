import path from 'path';
import HtmlWebpackPlugin from 'html-webpack-plugin';
import { fileURLToPath } from 'url';
import { dirname } from 'path';
import Dotenv from 'dotenv-webpack';

const __filename = fileURLToPath(import.meta.url);
const __dirname = dirname(__filename);

const isDocker = process.env.DOCKER === 'true';
const backendHost = isDocker ? 'backend' : 'localhost';

export default {
  entry: './src/index.tsx',
  module: {
    rules: [
      {
        test: /\.tsx?$/,
        use: 'ts-loader',
        exclude: /node_modules/,
      },

      //CSS
      {
        test: /\.css$/,
        use: ['style-loader', 'css-loader'],
      },

      //SCSS
      {
        test: /\.scss$/,
        use: ['style-loader', 'css-loader', 'sass-loader'],
      },
      {
        test: /\.(png|svg|jpg|gif)$/,
        use: ['file-loader'],
      },
    ],
  },
  resolve: {
    extensions: ['.tsx', '.ts', '.js'],
    alias: {
      src: path.resolve(__dirname, 'src'),
    },
  },
  output: {
    filename: '[name].[contenthash].js',
    path: path.resolve(__dirname, 'dist'),
    clean: true,
  },
  plugins: [
    new HtmlWebpackPlugin({
      template: path.resolve(__dirname, 'public', 'index.html'),
    }),
    new Dotenv({
      path: `.env.${process.env.NODE_ENV}`,
    }),
  ],
  devServer: {
    static: {
      directory: path.resolve(__dirname, 'public'),
    },
    historyApiFallback: true,
    hot: true,
    port: 3000,
    open: true,
    watchFiles: ['src/**/*'],
    client: {
      overlay: true,
      progress: true
    },
    proxy: [
      {
        context: ['/api'],
        target: `http://${backendHost}:8001`,
        changeOrigin: true,
        secure: false
      },
      {
        context: ['/ws/chat'],
        target: `ws://${backendHost}:8001`,
        ws: true,
        changeOrigin: true,
        secure: false
      }
    ]
  }
};