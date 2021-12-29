import os
from django.core.management.base import BaseCommand
from garpixcms.settings import MEDIA_ROOT
from photo.models import Photo


def str_list(seq):
    return '\n'.join(seq)


class Command(BaseCommand):
    help = 'Удалить неиспользуемые фото'

    def add_arguments(self, parser):
        parser.add_argument('-di', '--delete_instance', action='store_true',
                            help='Удаляет из базы фотографии у которых image=Null', )
        parser.add_argument('-s', '--show', action='store_true',
                            help='Не удаляет ни файлы, ни записи в базе данных. Выводит полный список файлов', )

    def handle(self, *args, **kwargs):
        show = kwargs.get("show")
        delete_instance = kwargs.get("delete_instance")
        photos = Photo.objects.all()
        print(f"Количество записей в БД: {photos.count()}")
        use_files = []
        file_not_exist = []
        inst_deleted = []
        for photo in photos:
            try:
                small_fp = photo.image_small.path
                use_files.append(small_fp)
                image_fp = photo.image.path
                use_files.append(image_fp)
            except ValueError:
                file_not_exist.append(
                    f"Файл изображения не существует id:{photo.id} название: {photo.title} путь: Null")
                if delete_instance is True and show is False:
                    inst_deleted.append(photo)
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
        print(f"Количество файлов записаных в БД: {len(use_files)}")
        print(f"Количество всех файлов: {len(result)}")
        print(f"Количество записей в бд без файлов: {len(file_not_exist)}")
        if file_not_exist:
            print("    Для удаления этих записей выполните: ./manage.py photo_del -di")
        if show:
            print(f"Количество файлов которые можно удалить: {len(delete)}")
            print(f"Файлы которые записаны в БД: \n{str_list(use_files)}")
            print(f"Все файлы: \n{str_list(result)}")
            print(f"Файлы которые можно удалить: \n{str_list(delete)}")
            print(f"Не прописан файл в БД: \n{str_list(file_not_exist)}")
        else:
            print(f"Количество файлов которые будут удалены: {len(delete)}")
            if delete:
                print(f"Файлы которые были удалены: \n{str_list(delete)}")
        if delete_instance:
            # objects = set(inst_deleted)
            for i in range(len(inst_deleted)):
                photo = inst_deleted.pop()
                try:
                    print(f"Запись была удалена id:{photo.id} название: {photo.title} путь:{photo.image_small.path}")
                except ValueError:
                    print(f"Запись была удалена id:{photo.id} название: {photo.title} путь: Null")
                photo.delete()
