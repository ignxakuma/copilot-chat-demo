FROM node:20-slim

WORKDIR /app

# The wildcard ensures it works even if package-lock.json is missing
COPY package*.json ./
RUN npm install

COPY . .

EXPOSE 3000

CMD ["npm", "run", "dev"]