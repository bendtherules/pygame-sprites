import pygame
from operator import truth


ANCHOR_TOPLEFT = 101
ANCHOR_TOPRIGHT = 102
ANCHOR_BOTTOMLEFT = 103
ANCHOR_BOTTOMRIGHT = 104
ANCHOR_CENTER = 105


class Sprite(object):
    """simple base class for visible game objects

    pygame.sprite.Sprite(*groups): return Sprite

    The base class for visible game objects. Derived classes will want to
    override the Sprite.update() method and assign Sprite.image and Sprite.rect
    attributes.  The initializer can accept any number of Group instances that
    the Sprite will become a member of.

    When subclassing the Sprite class, be sure to call the base initializer
    before adding the Sprite to Groups.

    """

    def __init__(self, *groups):
        self.image = None
        self.rect = None

        self.anchor = ANCHOR_TOPLEFT
        self.position = None

        self.dirty = False

        # visual attributes
        self.scale = 1
        self.rotate = 0
        self.visible = True

        self.__g = {}  # The groups the sprite is in
        if groups:
            self.add(*groups)

    def draw(self, surface):
        if (self.visible):
            return surface.blit(self.image, self.rect)
        else:
            return 0

    # a callback that gets called on any visual change
    def _visual_set(method):
        def wrapper(self, *args, **kwargs):
            result = method(self, *args, **kwargs)
            self.dirty = True
            if hasattr(self, 'on_visual_set'):
                self.on_visual_set(method, *args, **kwargs)
            return result
        return wrapper

    def _get_image(self):
        try:
            img = self._image
        except AttributeError:
            img = None

        if img is not None:
            if self.scale != 1 or self.rotate != 0:
                if self.scale != 1:
                    img = pygame.transform.scale(img, self.scaled_size())
                if self.rotate != 0:
                    img = pygame.transform.rotate(img, self.rotate)
                self.rect = img.get_rect()
                self.position = self.position

        return img

    def _set_image(self, img):
        self._image = img

    image = property(_get_image,
                     _visual_set(_set_image),
                     doc="The sprite's image to draw")

    #TODO handle negative values
    #TODO use same constants as Rect's
    def anchor_value(self):
        if type(self.anchor) is tuple:
            return self.anchor
        elif self.anchor == ANCHOR_TOPLEFT:
            return (0, 0)
        elif self.anchor == ANCHOR_TOPRIGHT:
            return (self.rect.width, 0)
        elif self.anchor == ANCHOR_BOTTOMLEFT:
            return (0, self.rect.height)
        elif self.anchor == ANCHOR_BOTTOMRIGHT:
            return (self.rect.width, self.rect.height)
        elif self.anchor == ANCHOR_CENTER:
            return (self.rect.width / 2, self.rect.height / 2)
        else:
            return None  # shouldn't happen :(

    def _get_position(self):
        return self._position

    #TODO handle float values
    def _set_position(self, value):
        self._position = value
        if value:
            (x, y) = value
            (anchor_x, anchor_y) = self.anchor_value()
            self.rect.topleft = (x - anchor_x, y - anchor_y)

    position = property(_get_position,
                        _visual_set(_set_position),
                        doc="The sprite's designated position, \
                        that is, where on the surface its anchor \
                        would be rendered")

    def _get_visible(self):
        return self._visible

    def _set_visible(self, value):
        self._visible = value

    visible = property(_get_visible,
                       _visual_set(_set_visible),
                       doc="Whether to draw the sprite")

    def _get_scale(self):
        return self._scale

    def _set_scale(self, ratio):
        if ratio < 0:
            raise AttributeError("ratio must be a positive float")
        self._scale = ratio

    scale = property(_get_scale,
                     _visual_set(_set_scale),
                     doc="A float representing the ratio between the \
                     original image's size and the size rendered")

    def scaled_size(self):
        (width, height) = self._image.get_size()
        width = (int)(width * self.scale)
        height = (int)(height * self.scale)
        return (width, height)

    def _get_rotate(self):
        try:
            return self._rotate
        except AttributeError:
            return 0

    def _set_rotate(self, degree):
        self._rotate = degree % 360  # TODO magic number?

    rotate = property(_get_rotate,
                      _visual_set(_set_rotate),
                      doc="The degrees by which to rotate the sprite's image")

    def add(self, *groups):
        """add the sprite to groups

        Sprite.add(*groups): return None

        Any number of Group instances can be passed as arguments. The
        Sprite will be added to the Groups it is not already a member of.

        """
        has = self.__g.__contains__
        for group in groups:
            if hasattr(group, '_spritegroup'):
                if not has(group):
                    group.add_internal(self)
                    self.add_internal(group)
            else:
                self.add(*group)

    def remove(self, *groups):
        """remove the sprite from groups

        Sprite.remove(*groups): return None

        Any number of Group instances can be passed as arguments. The Sprite
        will be removed from the Groups it is currently a member of.

        """
        has = self.__g.__contains__
        for group in groups:
            if hasattr(group, '_spritegroup'):
                if has(group):
                    group.remove_internal(self)
                    self.remove_internal(group)
            else:
                self.remove(*group)

    def add_internal(self, group):
        self.__g[group] = 0

    def remove_internal(self, group):
        del self.__g[group]

    def update(self, *args):
        """method to control sprite behavior

        Sprite.update(*args):

        The default implementation of this method does nothing; it's just a
        convenient "hook" that you can override. This method is called by
        Group.update() with whatever arguments you give it.

        There is no need to use this method if not using the convenience
        method by the same name in the Group class.

        """
        pass

    def kill(self):
        """remove the Sprite from all Groups

        Sprite.kill(): return None

        The Sprite is removed from all the Groups that contain it. This won't
        change anything about the state of the Sprite. It is possible to
        continue to use the Sprite after this method has been called, including
        adding it to Groups.

        """
        for c in self.__g:
            c.remove_internal(self)
        self.__g.clear()

    def groups(self):
        """list of Groups that contain this Sprite

        Sprite.groups(): return group_list

        Returns a list of all the Groups that contain this Sprite.

        """
        return list(self.__g)

    def alive(self):
        """does the sprite belong to any groups

        Sprite.alive(): return bool

        Returns True when the Sprite belongs to one or more Groups.
        """
        return truth(self.__g)

    def __repr__(self):
        return "<%s sprite(in %d groups)>" \
                % (self.__class__.__name__, len(self.__g))


class AggregatedSprite(Sprite):
    def _get_sprites(self):
        try:
            return self._sprites
        except AttributeError:
            self._sprites = []
            return self._sprites

    def _set_sprites(self, sprites):
        self._sprites = sprites

    def add_sprite(self, sprite):
        self.sprites.append(sprite)

    sprites = property(_get_sprites,
                       _set_sprites,
                       doc="List of sprites to aggregate")

    def draw(self, surface):
        ret = pygame.Rect(0, 0, 0, 0)
        for spr in self.sprites:
            r = spr.draw(surface)
            if r != 0:
                ret.union_ip(r)
        return ret

    def on_visual_set(self, method, *args, **kwargs):
        for spr in self.sprites:
            method(spr, *args, **kwargs)


class AbstractGroup(object):
    """base class for containers of sprites

    AbstractGroup does everything needed to behave as a normal group. You can
    easily subclass a new group class from this or the other groups below if
    you want to add more features.

    Any AbstractGroup-derived sprite groups act like sequences and support
    iteration, len, and so on.

    """

    # dummy val to identify sprite groups, and avoid infinite recursion
    _spritegroup = True

    def __init__(self):
        self.spritedict = {}
        self.lostsprites = []

    def sprites(self):
        """get a list of sprites in the group

        Group.sprite(): return list

        Returns an object that can be looped over with a 'for' loop. (For now,
        it is always a list, but this could change in a future version of
        pygame.) Alternatively, you can get the same information by iterating
        directly over the sprite group, e.g. 'for sprite in group'.

        """
        return list(self.spritedict)

    def add_internal(self, sprite):
        self.spritedict[sprite] = 0

    def remove_internal(self, sprite):
        r = self.spritedict[sprite]
        if r is not 0:
            self.lostsprites.append(r)
        del self.spritedict[sprite]

    def has_internal(self, sprite):
        return sprite in self.spritedict

    def copy(self):
        """copy a group with all the same sprites

        Group.copy(): return Group

        Returns a copy of the group that is an instance of the same class
        and has the same sprites in it.

        """
        return self.__class__(self.sprites())

    def __iter__(self):
        return iter(self.sprites())

    def __contains__(self, sprite):
        return self.has(sprite)

    def add(self, *sprites):
        """add sprite(s) to group

        Group.add(sprite, list, group, ...): return None

        Adds a sprite or sequence of sprites to a group.

        """
        for sprite in sprites:
            # It's possible that some sprite is also an iterator.
            # If this is the case, we should add the sprite itself,
            # and not the iterator object.
            if isinstance(sprite, Sprite):
                if not self.has_internal(sprite):
                    self.add_internal(sprite)
                    sprite.add_internal(self)
            else:
                try:
                    # See if sprite is an iterator, like a list or sprite
                    # group.
                    self.add(*sprite)
                except (TypeError, AttributeError):
                    # Not iterable. This is probably a sprite that is not an
                    # instance of the Sprite class or is not an instance of a
                    # subclass of the Sprite class. Alternately, it could be an
                    # old-style sprite group.
                    if hasattr(sprite, '_spritegroup'):
                        for spr in sprite.sprites():
                            if not self.has_internal(spr):
                                self.add_internal(spr)
                                spr.add_internal(self)
                    elif not self.has_internal(sprite):
                        self.add_internal(sprite)
                        sprite.add_internal(self)

    def remove(self, *sprites):
        """remove sprite(s) from group

        Group.remove(sprite, list, or group, ...): return None

        Removes a sprite or sequence of sprites from a group.

        """
        # This function behaves essentially the same as Group.add. It first
        # tries to handle each argument as an instance of the Sprite class. If
        # that failes, then it tries to handle the argument as an iterable
        # object. If that failes, then it tries to handle the argument as an
        # old-style sprite group. Lastly, if that fails, it assumes that the
        # normal Sprite methods should be used.
        for sprite in sprites:
            if isinstance(sprite, Sprite):
                if self.has_internal(sprite):
                    self.remove_internal(sprite)
                    sprite.remove_internal(self)
            else:
                try:
                    self.remove(*sprite)
                except (TypeError, AttributeError):
                    if hasattr(sprite, '_spritegroup'):
                        for spr in sprite.sprites():
                            if self.has_internal(spr):
                                self.remove_internal(spr)
                                spr.remove_internal(self)
                    elif self.has_internal(sprite):
                        self.remove_internal(sprite)
                        sprite.remove_internal(self)

    def has(self, *sprites):
        """ask if group has a sprite or sprites

        Group.has(sprite or group, ...): return bool

        Returns True if the given sprite or sprites are contained in the
        group. Alternatively, you can get the same information using the
        'in' operator, e.g. 'sprite in group', 'subgroup in group'.

        """
        return_value = False

        for sprite in sprites:
            if isinstance(sprite, Sprite):
                # Check for Sprite instance's membership in this group
                if self.has_internal(sprite):
                    return_value = True
                else:
                    return False
            else:
                try:
                    if self.has(*sprite):
                        return_value = True
                    else:
                        return False
                except (TypeError, AttributeError):
                    if hasattr(sprite, '_spritegroup'):
                        for spr in sprite.sprites():
                            if self.has_internal(spr):
                                return_value = True
                            else:
                                return False
                    else:
                        if self.has_internal(sprite):
                            return_value = True
                        else:
                            return False

        return return_value

    def update(self, *args):
        """call the update method of every member sprite

        Group.update(*args): return None

        Calls the update method of every member sprite. All arguments that
        were passed to this method are passed to the Sprite update function.

        """
        for s in self.sprites():
            s.update(*args)

    def draw(self, surface):
        """draw all sprites onto the surface

        Group.draw(surface): return None

        Draws all of the member sprites onto the given surface.

        """
        sprites = self.sprites()
        surface_blit = surface.blit
        for spr in sprites:
            if (hasattr(spr, 'draw')):
                self.spritedict[spr] = spr.draw(surface)
            else:
                self.spritedict[spr] = surface_blit(spr.image, spr.rect)
        self.lostsprites = []

    def clear(self, surface, bgd):
        """erase the previous position of all sprites

        Group.clear(surface, bgd): return None

        Clears the area under every drawn sprite in the group. The bgd
        argument should be Surface which is the same dimensions as the
        screen surface. The bgd could also be a function which accepts
        the given surface and the area to be cleared as arguments.

        """
        if callable(bgd):
            for r in self.lostsprites:
                bgd(surface, r)
            for r in self.spritedict.values():
                if r is not 0:
                    bgd(surface, r)
        else:
            surface_blit = surface.blit
            for r in self.lostsprites:
                surface_blit(bgd, r, r)
            for r in self.spritedict.values():
                if r is not 0:
                    surface_blit(bgd, r, r)

    def empty(self):
        """remove all sprites

        Group.empty(): return None

        Removes all the sprites from the group.

        """
        for s in self.sprites():
            self.remove_internal(s)
            s.remove_internal(self)

    def __nonzero__(self):
        return truth(self.sprites())

    def __len__(self):
        """return number of sprites in group

        Group.len(group): return int

        Returns the number of sprites contained in the group.

        """
        return len(self.sprites())

    def __repr__(self):
        return "<%s(%d sprites)>" % (self.__class__.__name__, len(self))


class Group(AbstractGroup):
    """container class for many Sprites

    pygame.sprite.Group(*sprites): return Group

    A simple container for Sprite objects. This class can be subclassed to
    create containers with more specific behaviors. The constructor takes any
    number of Sprite arguments to add to the Group. The group supports the
    following standard Python operations:

        in      test if a Sprite is contained
        len     the number of Sprites contained
        bool    test if any Sprites are contained
        iter    iterate through all the Sprites

    The Sprites in the Group are not ordered, so the Sprites are drawn and
    iterated over in no particular order.

    """
    def __init__(self, *sprites):
        AbstractGroup.__init__(self)
        self.add(*sprites)

RenderPlain = Group
RenderClear = Group
