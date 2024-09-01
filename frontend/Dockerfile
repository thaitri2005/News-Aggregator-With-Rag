# Dockerfile for Frontend
FROM node:18

# Set working directory
WORKDIR /frontend

# Copy package.json and install dependencies
COPY package*.json ./
RUN npm install

# Copy the rest of the application code
COPY . .

# Expose port 3000 and start the app
EXPOSE 3000
CMD ["npm", "start"]
