%bcond_without openmpi
%bcond_without mpich

Name:           mfem
Version:        4.5.2
Release:        %autorelease
Summary:        Lightweight, general, scalable C++ library for finite element methods

# The main license is under BSD-3-Clause, but some files are under other licenses:
# AmgXWrapper (linalg/amgxsolver.{hpp,cpp}) -- MIT license
# Catch++ (tests/unit/catch.hpp) -- Boost 1.0 license
# Gecko (general/gecko.{cpp,hpp}) -- BSD 3-clause license
# Picojson (fem/picojson.h) -- Custom 2-clause license
# TinyXML2 (general/tinyxml2.{cpp,h}) -- zlib license
# Zstr (general/zstr.hpp) -- MIT license
License:        BSD-3-Clause AND MIT AND BSL-1.0 AND BSD-3-Clause AND BSD-2-Clause AND Zlib
URL:            https://github.com/mfem/mfem
Source0:        %{url}/archive/v%{version}/%{name}-%{version}.tar.gz
# Replace deprecated gethostbyname by getaddrinfo
Patch1:         https://github.com/mfem/mfem/pull/3685.patch

BuildRequires:  gcc-c++
BuildRequires:  cmake
BuildRequires:  ninja-build
BuildRequires:  flexiblas-devel
BuildRequires:  metis-devel

Provides:       bundled(AmgXWrapper)
Provides:       bundled(catch2) = 2.13.9
Provides:       bundled(gecko)
Provides:       bundled(picojson)
Provides:       bundled(tinyxml2)
Provides:       bundled(zstr)

%description
MFEM is a modular parallel C++ library for finite element methods. Its goal is
to enable high-performance scalable finite element discretization research and
application development on a wide variety of platforms, ranging from laptops to
supercomputers.

%package        devel
Summary:        Development files for %{name}
Requires:       %{name}%{?_isa} = %{version}-%{release}

%description    devel
This package contains libraries and header files for
developing applications that use %{name}.

%if %{with openmpi}
%package        openmpi
Summary:        OpenMPI version of %{name}
BuildRequires:  openmpi-devel
BuildRequires:  hypre-openmpi-devel
Requires:       openmpi%{?_isa}

%description openmpi
This package contains the %{name} library compiled against OpenMPI.

%package        openmpi-devel
Summary:        Development files for OpenMPI version of %{name}
Requires:       %{name}-openmpi%{?_isa} = %{version}-%{release}
Requires:       openmpi-devel%{?_isa}

%description openmpi-devel
This package contains the %{name} development library compiled
against OpenMPI.
%endif

%if %{with mpich}
%package        mpich
Summary:        MPICH version of %{name}
BuildRequires:  mpich-devel
BuildRequires:  hypre-mpich-devel
Requires:       mpich%{?_isa}

%description mpich
This package contains the %{name} library compiled against MPICH.

%package        mpich-devel
Summary:        Development libraries for MPICH version of %{name}
Requires:       %{name}-mpich%{?_isa} = %{version}-%{release}
Requires:       mpich-devel%{?_isa}

%description mpich-devel
This package contains the %{name} development library compiled
against MPICH.
%endif

%prep
%autosetup -p1

%build
OPTIONS=(
    -G Ninja \
    -DCMAKE_SKIP_BUILD_RPATH=OFF \
    -DCMAKE_SKIP_INSTALL_RPATH=ON \
    -DMFEM_ENABLE_TESTING=ON \
    -DMFEM_ENABLE_EXAMPLES=OFF \
    -DMFEM_ENABLE_MINIAPPS=OFF \
    -DMFEM_ENABLE_GOOGLE_BENCHMARKS=OFF \
)

%global _vpath_builddir %{_target_platform}
%cmake \
    ${OPTIONS[@]} \
    -DINSTALL_LIB_DIR=%{_libdir} \
    -DINSTALL_INCLUDE_DIR=%{_includedir}/mfem \
    -DINSTALL_CMAKE_DIR=%{_libdir}/cmake/mfem \
    -DMFEM_USE_MPI=OFF \
# https://github.com/mfem/mfem/issues/3677#issuecomment-1553387055
%cmake_build --target exec

%if %{with openmpi}
%{_openmpi_load}
%global _vpath_builddir %{_target_platform}-openmpi
%cmake \
    ${OPTIONS[@]} \
    -DHYPRE_INCLUDE_DIR=${MPI_INCLUDE}/hypre \
    -DHYPRE_LIBRARY=${MPI_LIB}/libHYPRE.so \
    -DINSTALL_LIB_DIR=${MPI_LIB} \
    -DINSTALL_INCLUDE_DIR=${MPI_INCLUDE}/mfem \
    -DINSTALL_CMAKE_DIR=${MPI_LIB}/cmake/mfem \
    -DMFEM_USE_MPI=ON \
%cmake_build --target exec
%{_openmpi_unload}
%endif

%if %{with mpich}
%{_mpich_load}
%global _vpath_builddir %{_target_platform}-mpich
%cmake \
    ${OPTIONS[@]} \
    -DHYPRE_INCLUDE_DIR=${MPI_INCLUDE}/hypre \
    -DHYPRE_LIBRARY=${MPI_LIB}/libHYPRE.so \
    -DINSTALL_LIB_DIR=${MPI_LIB} \
    -DINSTALL_INCLUDE_DIR=${MPI_INCLUDE}/mfem \
    -DINSTALL_CMAKE_DIR=${MPI_LIB}/cmake/mfem \
    -DMFEM_USE_MPI=ON \
%cmake_build --target exec
%{_mpich_unload}
%endif

%install
%global _vpath_builddir %{_target_platform}
%cmake_install

%if %{with openmpi}
%{_openmpi_load}
%global _vpath_builddir %{_target_platform}-openmpi
%cmake_install
%{_openmpi_unload}
%endif

%if %{with mpich}
%{_mpich_load}
%global _vpath_builddir %{_target_platform}-mpich
%cmake_install
%{_mpich_unload}
%endif

%check
%global _vpath_builddir %{_target_platform}
# https://download.copr.fedorainfracloud.org/results/topazus/test/fedora-rawhide-s390x/06087817-mfem/builder-live.log.gz
# Converting between different byte orders is unsupported.
%ifarch s390x
%ctest -E unit_tests
%else
%ctest
%endif

%if %{with openmpi}
%{_openmpi_load}
%global _vpath_builddir %{_target_platform}-openmpi
%ifarch s390x
%ctest -E unit_tests
%else
%ctest
%endif
%{_openmpi_unload}
%endif

%if %{with mpich}
%{_mpich_load}
%global _vpath_builddir %{_target_platform}-mpich
%ifarch s390x
%ctest -E unit_tests
%else
%ctest
%endif
%{_mpich_unload}
%endif

%files
%license LICENSE
%doc README.md
%{_libdir}/libmfem.so.%{version}

%files devel
%{_includedir}/mfem/
%{_libdir}/cmake/mfem/
%{_libdir}/libmfem.so
%dir %{_datadir}/mfem
%{_datadir}/mfem/config.mk
%{_datadir}/mfem/test.mk

%if %{with openmpi}
%files openmpi
%license LICENSE
%doc README.md
%{_libdir}/openmpi/lib/libmfem.so.%{version}

%files openmpi-devel
%{_includedir}/openmpi-%{_arch}/
%{_libdir}/openmpi/lib/cmake/mfem/
%{_libdir}/openmpi/lib/libmfem.so
%endif

%if %{with mpich}
%files mpich
%license LICENSE
%doc README.md
%{_libdir}/mpich/lib/libmfem.so.%{version}

%files mpich-devel
%{_includedir}/mpich-%{_arch}/
%{_libdir}/mpich/lib/cmake/mfem/
%{_libdir}/mpich/lib/libmfem.so
%endif

%changelog
%autochangelog
