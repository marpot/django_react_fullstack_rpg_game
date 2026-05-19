import path from 'path';
import HtmlWebpackPlugin from 'html-webpack-plugin';
import { fileURLToPath } from 'url';
import { dirname } from 'path';
import Dotenv from 'dotenv-webpack';
import ReactRefreshWebpackPlugin from '@pmmmwh/react-refresh-webpack-plugin';
import reactRefreshTypeScript from 'react-refresh-typescript';

const __filename = fileURLToPath(import.meta.url);
const __dirname = dirname(__filename);

const isDev = process.env.NODE_ENV === 'development';
const isDocker = process.env.DOCKER === 'true';
const backendHost = isDocker ? 'backend' : 'localhost';

export default {
  mode: isDev ? 'development' : 'production',

  entry: './src/index.tsx',

  module: {
    rules: [
      {
        test: /\.tsx?$/,
        exclude: /node_modules/,
        use: {
          loader: 'ts-loader',
          options: {
            transpileOnly: true,
            getCustomTransformers: () => ({
              before: isDev
                ? [reactRefreshTypeScript()]
                : [],
            }),
          },
        },
      },

      // CSS
      {
        test: /\.css$/,
        use: ['style-loader', 'css-loader'],
      },

      // SCSS
      {
        test: /\.scss$/,
        use: ['style-loader', 'css-loader', 'sass-loader'],
      },

      // assets
      {
        test: /\.(png|svg|jpg|gif)$/,
        type: 'asset/resource',
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
    filename: isDev ? '[name].js' : '[name].[contenthash].js',
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

    isDev && new ReactRefreshWebpackPlugin(),
  ].filter(Boolean),

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
      progress: true,
    },

    proxy: [
      {
        context: ['/api'],
        target: `http://${backendHost}:8001`,
        changeOrigin: true,
        secure: false,
      },
      {
        context: ['/ws/chat'],
        target: `ws://${backendHost}:8001`,
        ws: true,
        changeOrigin: true,
        secure: false,
      },
    ],
  },
};