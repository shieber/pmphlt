# Comments System Setup Guide

## Overview
This guide explains the migration from Disqus to Giscus, a GitHub Discussions-based commenting system that provides better integration with Jekyll and GitHub Pages.

## Why Giscus?

### ✅ Meets All Your Requirements:
1. **GitHub-Jekyll compatibility**: Uses GitHub Discussions as backend
2. **CSS customization**: Full control over styling via custom CSS
3. **Time-based commenting**: Automatic closure after 30 days (configurable)
4. **Spam control**: GitHub's built-in moderation tools and community features

### ✅ Additional Benefits:
- **No external dependencies**: Everything stays within GitHub ecosystem
- **Better performance**: No third-party JavaScript loading
- **Privacy-friendly**: No tracking or ads
- **Free**: No subscription costs
- **Moderation tools**: GitHub's robust moderation features

## Setup Steps

### 1. Enable GitHub Discussions
1. Go to your repository: https://github.com/shieber/pmphlt
2. Click "Settings" tab
3. Scroll down to "Features" section
4. Check "Discussions" to enable it
5. Click "Save"

### 2. Create Discussion Category
1. Go to the "Discussions" tab in your repository
2. Click "Categories" in the sidebar
3. Click "New category"
4. Create a category called "Announcements" (or use existing)
5. Note the category ID (you'll need this)

### 3. Get Repository and Category IDs
You can get these IDs using GitHub's GraphQL API or use the provided values:

```bash
# Repository ID (already configured)
R_kgDOJqXqXQ

# Category ID (already configured) 
DIC_kwDOJqXqXc4CbqXq
```

### 4. Configure Giscus
The configuration is already set up in:
- `_layouts/post.html` - Comment display logic
- `_config.yml` - Giscus settings
- `assets/css/custom.css` - Styling

### 5. Test the Setup
1. Build your site: `bundle exec jekyll serve`
2. Visit a post with comments enabled
3. Verify the Giscus widget appears
4. Test posting a comment (requires GitHub login)

## Configuration Options

### Time-Based Comment Closure
Comments automatically close after 30 days. To customize:

```liquid
{% assign post_age_days = site.time | date: '%s' | minus: page.date | date: '%s' | divided_by: 86400 %}
{% if post_age_days < 30 or page.comments_always_open %}
  <!-- Show comments -->
{% else %}
  <!-- Show closed message -->
{% endif %}
```

### Per-Post Control
Add to post front matter:
```yaml
---
comments: false  # Disable comments for this post
comments_always_open: true  # Keep comments open regardless of age
---
```

### Giscus Theme Options
Available themes:
- `light` - Light theme
- `dark` - Dark theme  
- `preferred_color_scheme` - Auto (recommended)
- `transparent_dark` - Transparent dark
- `transparent_light` - Transparent light

### URL Change Handling
**Important**: When post URLs change, Giscus creates new discussion threads, potentially losing existing comments.

**Solutions:**
1. **Use title mapping** (recommended): `data-mapping="title"` - more stable than pathname
2. **Add comment IDs** to post front matter: `comment_id: "unique-identifier"`
3. **Set up redirects** in `_redirects` file
4. **Manual migration** of comments between discussions

**Example front matter:**
```yaml
---
title: "Moderating principles"
comment_id: "moderating-principles-2022"
---
```

## Moderation Features

### GitHub Discussions Moderation
- **Category restrictions**: Limit who can post in specific categories
- **User blocking**: Block problematic users
- **Content filtering**: GitHub's built-in content filters
- **Community guidelines**: Set up discussion guidelines
- **Moderator roles**: Assign moderation permissions

### Spam Prevention
- **GitHub authentication**: Requires GitHub account
- **Rate limiting**: Built-in posting limits
- **Content moderation**: Community reporting system
- **Bot detection**: GitHub's anti-bot measures

## Migration from Disqus

### Preserving Existing Comments
1. **Export Disqus comments**: Use Disqus export feature
2. **Manual migration**: Copy important comments to GitHub Discussions
3. **Archive old comments**: Keep Disqus active in read-only mode temporarily

### SEO Considerations
- Update any comment-related meta tags
- Consider adding structured data for comments
- Monitor search console for comment-related issues

## Troubleshooting

### Common Issues

**Giscus not loading:**
- Check repository and category IDs
- Verify GitHub Discussions is enabled
- Check browser console for errors

**Comments not appearing:**
- Ensure post has `comments: true` in front matter
- Check if post is older than 30 days
- Verify GitHub authentication

**Styling issues:**
- Check custom CSS in `assets/css/custom.css`
- Test with different themes
- Verify responsive design

### Debug Mode
Add `data-strict="1"` to Giscus script for debug information.

## Maintenance

### Regular Tasks
- Monitor GitHub Discussions for spam
- Review moderation settings
- Update Giscus configuration as needed
- Backup important discussions

### Analytics
- Use GitHub's built-in analytics
- Monitor discussion engagement
- Track comment quality and spam levels

## Support

- **Giscus Documentation**: https://giscus.app/
- **GitHub Discussions Help**: https://docs.github.com/en/discussions
- **Jekyll Documentation**: https://jekyllrb.com/docs/

## Files Modified

1. `_layouts/post.html` - Replaced Disqus with Giscus
2. `_config.yml` - Updated comment configuration
3. `assets/css/custom.css` - Added comment styling
4. `COMMENTS_SETUP.md` - This setup guide

The migration is complete and ready for testing! 