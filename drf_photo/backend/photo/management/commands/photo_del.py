import os
from django.core.management.base import BaseCommand
from garpixcms.settings import MEDIA_ROOT
from photo.models import Photo


class Command(BaseCommand):
    help = 'Удалить неиспользуемые фото'

    def add_arguments(self, parser):
        parser.add_argument('-di', '--delete_instance', action='store_true', help='Удаляет из базы фотографии у которых image=Null', )
        parser.add_argument('-s', '--show', action='store_true', help='Не удаляет ни файлы, ни записи в базе данных. Выводит полный список файлов', )

    def handle(self, *args, **kwargs):
        show = kwargs.get("show")
        delete_instance = kwargs.get("delete_instance")
        photos = Photo.objects.all()
        self.stdout.write(f"Количество записей в БД: {photos.count()}", ending='\n')
        use_files = []
        file_not_exist = []
        inst_deleted = []
        for photo in photos:
            try:
                small_fp = photo.image_small.path
                use_files.append(small_fp)
                image_fp = photo.image.path
                use_files.append(image_fp)
                # if os.path.exists(small_fp):
                #     use_files.append(small_fp)
                # else:
                #     file_not_exist.append(f"Файл миниатюры не существует id:{photo.id} название: {photo.title} путь:{photo.image_small.path}")
                #     if delete_instance is True and show is False:
                #         inst_deleted.append(photo)
                # if os.path.exists(image_fp):
                #     use_files.append(image_fp)
                # else:
                #     file_not_exist.append(f"Файл изображения не существует id:{photo.id} название: {photo.title} путь:{photo.image.path}")
                #     if delete_instance is True and show is False:
                #         inst_deleted.append(photo)
            except ValueError:
                file_not_exist.append(f"Файл изображения не существует id:{photo.id} название: {photo.title} путь: Null")
                if delete_instance is True and show is False:
                    inst_deleted.append(photo)
        # use_files = set(use_files)
        # file_not_exist = set(file_not_exist)
        walk = os.walk(os.path.abspath(MEDIA_ROOT), topdown=True, onerror=None, followlinks=False)
        result = []
        delete = []
        for d, dirs, files in walk:
            for f in files:
                path = os.path.join(d, f)
                path = os.path.abspath(path)
                result.append(path)
                if path not in use_files:
                    delete.append(path)
                    if show is False:
                        os.remove(path)
        # result = set(result)
        # delete = set(delete)
        delete_str = '\n'.join(delete)
        if show:
            uses_str = '\n'.join(use_files)
            all_str = '\n'.join(result)
            file_not_exist_str = '\n'.join(file_not_exist)
        self.stdout.write(f"Количество файлов записаных в БД: {len(use_files)}", ending='\n')
        self.stdout.write(f"Количество всех файлов: {len(result)}", ending='\n')
        self.stdout.write(f"Количество записей в бд без файлов: {len(file_not_exist)}", ending='\n')
        if file_not_exist:
            self.stdout.write("    Для удаления этих записей выполните: ./manage.py photo_del -di", ending='\n')
        if show:
            self.stdout.write(f"Количество файлов которые можно удалить: {len(delete)}", ending='\n')
            self.stdout.write(f"Файлы которые записаны в БД: \n{uses_str}", ending='\n')
            self.stdout.write(f"Все файлы: \n{all_str}", ending='\n')
            self.stdout.write(f"Файлы которые можно удалить: \n{delete_str}", ending='\n')
            self.stdout.write(f"Не прописан файл в БД: \n{file_not_exist_str}", ending='\n')
        else:
            self.stdout.write(f"Количество файлов которые будут удалены: {len(delete)}", ending='\n')
            if delete:
                self.stdout.write(f"Файлы которые были удалены: \n{delete_str}", ending='\n')
        if delete_instance:
            objects = set(inst_deleted)
            for i in range(len(objects)):
                photo = objects.pop()
                try:
                    self.stdout.write(f"Запись была удалена id:{photo.id} название: {photo.title} путь:{photo.image_small.path}", ending='\n')
                except ValueError:
                    self.stdout.write(f"Запись была удалена id:{photo.id} название: {photo.title} путь: Null", ending='\n')
                photo.delete()
