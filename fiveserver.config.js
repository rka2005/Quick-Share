// Five Server configuration
// Only watch frontend files to prevent auto-reloading when uploaded files are saved in backend/uploads
module.exports = {
  watch: ['frontend'],
  ignore: [
    'backend',
    'backend/**',
    '**/uploads/**',
    'uploads/**',
    '.git/**',
    '.vscode/**',
    '**/*.txt',
    '**/*.pdf',
    '**/*.png',
    '**/*.jpg',
    '**/*.jpeg',
    '**/*.webp'
  ]
};
