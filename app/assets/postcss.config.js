module.exports = {
    ident: 'postcss-loader',
    syntax: 'postcss-scss',
    plugins: [
        require('postcss-easy-import'),
        require('postcss-advanced-variables'),
        require('postcss-atroot'),
        require('postcss-extend-rule'),
        require('postcss-preset-env')({
            features: {
                'nesting-rules': false
            }
        }),
        require('postcss-property-lookup'),
        require('postcss-rem')({baseline: 18, fallback: true}),
        require('postcss-focus-visible'),
        require('postcss-css-variables'),
        require('postcss-map-get'),
        require('tailwindcss/nesting'),
        require('tailwindcss'),
        require('autoprefixer')({
            grid: 'autoplace'
        }),
        require('cssnano')({
            preset: 'default',
        })
    ]
}
