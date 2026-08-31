from django.shortcuts import render, get_object_or_404, redirect
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView, UpdateView as BaseUpdateView
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib import messages
from django.urls import reverse_lazy, reverse
from django.utils import timezone
from django.views import View
from django.http import HttpResponseForbidden
from django import forms
from tinymce.widgets import TinyMCE

from django.db.models import Q
from .models import BlogPost, BlogComment
from .forms import CommentForm

# Create a custom form for BlogPost with TinyMCE
class BlogPostForm(forms.ModelForm):
    content = forms.CharField(
        widget=TinyMCE(
            attrs={
                'required': True,
                'cols': 30,
                'rows': 10,
            }
        )
    )
    
    class Meta:
        model = BlogPost
        fields = ['title', 'category', 'content', 'excerpt', 'featured_image', 'tags', 'status']

class BlogPostListView(ListView):
    model = BlogPost
    template_name = 'blog.html'
    context_object_name = 'posts'
    paginate_by = 6
    
    def get_queryset(self):
        queryset = BlogPost.objects.filter(
            status='published',
            published_date__lte=timezone.now()
        ).select_related('author')
        
        # Filter by category
        category = self.request.GET.get('category')
        if category:
            queryset = queryset.filter(category__iexact=category)
            
        # Search functionality
        query = self.request.GET.get('q')
        if query:
            queryset = queryset.filter(
                Q(title__icontains=query) |
                Q(content__icontains=query) |
                Q(excerpt__icontains=query) |
                Q(tags__icontains=query)
            )
            
        return queryset
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Get all unique categories for the sidebar
        context['categories'] = BlogPost.objects.filter(
            status='published'
        ).values_list('category', flat=True).distinct()
        
        # Get recent posts for the sidebar
        context['recent_posts'] = BlogPost.objects.filter(
            status='published',
            published_date__lte=timezone.now()
        ).order_by('-published_date')[:5]
        
        # Get popular posts (most viewed)
        context['popular_posts'] = BlogPost.objects.filter(
            status='published'
        ).order_by('-view_count')[:3]
        
        # Add search query to context
        context['search_query'] = self.request.GET.get('q', '')
        context['current_category'] = self.request.GET.get('category', '')
        
        return context


class BlogPostDetailView(DetailView):
    model = BlogPost
    template_name = 'blog_detail.html'
    context_object_name = 'post'
    
    def get_queryset(self):
        return BlogPost.objects.filter(
            status='published',
            published_date__lte=timezone.now()
        )
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        post = self.get_object()
        
        # Increment view count
        post.increment_view_count()
        
        # Get related posts (same category)
        context['related_posts'] = BlogPost.objects.filter(
            category=post.category,
            status='published',
            published_date__lte=timezone.now()
        ).exclude(id=post.id)[:3]
        
        # Get comments for this post
        if self.request.user.is_staff:
            # Show all comments to staff users
            context['comments'] = post.comments.all().order_by('created_at')
        else:
            # Show only active comments to regular users
            context['comments'] = post.comments.filter(active=True).order_by('created_at')
            
        # Add active comments count to context
        context['active_comments_count'] = post.comments.filter(active=True).count()
        
        # For the comment form
        context['comment_form'] = CommentForm(initial={
            'post': post.id,
            'name': self.request.user.get_full_name() if self.request.user.is_authenticated else '',
            'email': self.request.user.email if self.request.user.is_authenticated else ''
        })
        
        # Add recent posts for sidebar
        context['recent_posts'] = BlogPost.objects.filter(
            status='published',
            published_date__lte=timezone.now()
        ).exclude(id=post.id).order_by('-published_date')[:5]
        
        # Add categories for sidebar
        context['categories'] = BlogPost.objects.filter(
            status='published'
        ).values_list('category', flat=True).distinct()
        
        # Add tags for the post
        context['tags'] = post.get_tags()
        
        return context
    
    # Comment submission is handled by the add_comment_to_post function view


class BlogPostCreateView(LoginRequiredMixin, UserPassesTestMixin, CreateView):
    model = BlogPost
    form_class = BlogPostForm
    template_name = 'blog_post_form.html'
    
    def form_valid(self, form):
        form.instance.author = self.request.user
        if 'publish' in self.request.POST:
            form.instance.published_date = timezone.now()
            form.instance.status = 'published'
        return super().form_valid(form)
    
    def get_success_url(self):
        messages.success(self.request, 'Blog post created successfully!')
        return reverse('core:blog_detail', kwargs={'slug': self.object.slug})
        
    def test_func(self):
        return self.request.user.is_staff


class BlogPostUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = BlogPost
    form_class = BlogPostForm
    template_name = 'blog_post_form.html'
    
    def form_valid(self, form):
        form.instance.author = self.request.user
        messages.success(self.request, 'Post updated successfully!')
        return super().form_valid(form)
        
    def test_func(self):
        post = self.get_object()
        return self.request.user == post.author or self.request.user.is_staff
        
    def get_success_url(self):
        messages.success(self.request, 'Your post has been updated!')
        return reverse_lazy('core:blog_detail', kwargs={'slug': self.object.slug})


class BlogPostDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    model = BlogPost
    template_name = 'blog_post_confirm_delete.html'
    success_url = reverse_lazy('core:blog')
    
    def test_func(self):
        post = self.get_object()
        return self.request.user == post.author or self.request.user.is_staff
        
    def delete(self, request, *args, **kwargs):
        messages.success(request, 'Post deleted successfully!')
        return super().delete(request, *args, **kwargs)


import logging
logger = logging.getLogger(__name__)

def add_comment_to_post(request, slug):
    post = get_object_or_404(BlogPost, slug=slug, status='published')
    
    if request.method == 'POST':
        logger.info(f"Received POST data: {request.POST}")
        form = CommentForm(request.POST)
        
        if form.is_valid():
            try:
                comment = form.save(commit=False)
                comment.post = post
                comment.active = True
                comment.save()
                logger.info(f"Comment saved successfully: {comment.id}")
                messages.success(request, 'Your comment has been submitted and is awaiting moderation.')
                return redirect('core:blog_detail', slug=post.slug)
            except Exception as e:
                logger.error(f"Error saving comment: {str(e)}")
                messages.error(request, 'There was an error saving your comment. Please try again.')
        else:
            logger.warning(f"Form validation failed: {form.errors}")
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f"{field}: {error}")
    else:
        form = CommentForm(initial={'post': post.id})
    
    # If we get here, the form was invalid or it's a GET request
    context = {
        'post': post,
        'comment_form': form,
        'comments': post.comments.filter(active=True).order_by('created_at'),
        'recent_posts': BlogPost.objects.filter(
            status='published',
            published_date__lte=timezone.now()
        ).exclude(id=post.id).order_by('-published_date')[:5],
        'categories': BlogPost.objects.filter(
            status='published'
        ).values_list('category', flat=True).distinct(),
        'tags': post.get_tags()
    }
    return render(request, 'blog_detail.html', context)


class CommentUpdateView(LoginRequiredMixin, UserPassesTestMixin, BaseUpdateView):
    model = BlogComment
    template_name = 'comment_edit.html'
    fields = ['name', 'email', 'body', 'active']
    
    def test_func(self):
        return self.request.user.is_staff
    
    def get_success_url(self):
        messages.success(self.request, 'Comment updated successfully.')
        return reverse('core:blog_detail', kwargs={'slug': self.object.post.slug})
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['post'] = self.object.post
        return context


class CommentDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    model = BlogComment
    template_name = 'comment_confirm_delete.html'
    
    def test_func(self):
        return self.request.user.is_staff
    
    def get_success_url(self):
        messages.success(self.request, 'Comment deleted successfully.')
        return reverse('core:blog_detail', kwargs={'slug': self.object.post.slug})
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['post'] = self.object.post
        return context
